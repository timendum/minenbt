"""Provides interfaces to handle specific Minecraft File"""
import zlib
from collections import namedtuple
from io import BytesIO
from math import ceil
from pathlib import Path
from typing import Dict, Iterator, Optional, Set, Tuple, Union

import numpy
from nbtlib import Compound
from nbtlib.tag import BYTE, INT, read_numeric

__all__ = ["AnvilFile"]


class _Metadata(namedtuple("_Metadata", ("offset", "timestamp"))):
    """A chunk metadata"""

    __slots__ = ()

    def is_valid(self) -> bool:
        """Returns true if the chunk is generated."""
        return self.offset != 0

    @property
    def seek(self) -> int:
        """Distance in byte from the beginning of the file."""
        return self.offset * 4096


class Section(Compound):
    """A 16×16×16 section of the chuck for DataVersion < 2529."""

    def __init__(self, compound) -> None:
        super().__init__(dict(compound))
        self._states: Optional[numpy.array] = None
        if "Palette" not in self:
            self._palette: Optional[Compound] = None
            return
        self._palette = [i for i in self["Palette"]]

    def block(self, x, y, z) -> Optional[Compound]:
        if not self._palette or self._states is None:
            return None
        return self._palette[self._states[y][z][x]]

    def blocks(self) -> Iterator[Compound]:
        if self._palette:
            for (y, z, x), state in numpy.ndenumerate(self._states):
                yield (x, y, z), self._palette[state]

    def blocks_available(self) -> Set[str]:
        if not self._palette:
            return set()
        return set([n["Name"] for n in self._palette])

    def find_block(self, x, y, z) -> Optional[Compound]:
        if not self._palette or self._states is None:
            return None
        x = x & 15
        y = y & 15
        z = z & 15
        return self._palette[self._states[y][z][x]]


_POW2 = [pow(2, i) for i in range(15, -1, -1)]
# max = 65535 (uint16)


class Section113(Section):
    """A 16×16×16 section of the chuck for DataVersion >= 2529.

    From Java Edition 1.13."""

    def __init__(self, compound) -> None:
        super().__init__(compound)
        if not self._palette:
            return
        # TODO byteorder
        nbit = max((len(self._palette) - 1).bit_length(), 4)
        # use native numpy array
        bstates = numpy.array(
            numpy.array(self["BlockStates"][::-1]).view(numpy.uint8), dtype=numpy.uint8
        )
        # convert BlockStates to unsigned integer and then to bits
        bstates = numpy.unpackbits(bstates)
        # split array in array for nbit long array
        splitted = bstates.reshape((-1, nbit))
        # convert array of bits to int
        states = (splitted * _POW2[-nbit:]).sum(axis=1)
        # reshape to xzy
        self._states = states[::-1].reshape(16, 16, 16)


class Section116(Section):
    """A 16×16×16 section of the chuck for DataVersion >= 2529.

    From Java Edition 20w17a (1.16 snapshot 2)."""

    def __init__(self, compound) -> None:
        super().__init__(compound)
        if not self._palette:
            return
        # TODO byteorder
        nbit = max((len(self._palette) - 1).bit_length(), 4)
        # check dimension
        if len(self["BlockStates"]) != ceil(16 * 16 * 16 / (64 // nbit)):
            raise ValueError(
                "There are {} 64-bit fields but {} states".format(
                    len(self["BlockStates"]), len(self._palette)
                )
            )
        unused = 64 % nbit
        blength = 64 - unused
        mask = pow(2, nbit) - 1
        states = []
        for longstate in self["BlockStates"]:
            # convert to unsigned
            longstate = longstate & 0xFFFFFFFFFFFFFFFF
            for i in range(0, blength, nbit):
                states.append(longstate & mask)
                longstate = longstate >> nbit
        self._states = numpy.reshape(states[: 16 * 16 * 16], [16, 16, 16]).tolist()


class Chunk(Compound):
    """Chunks store the terrain and entities within a 16×256×16 area.

    https://minecraft.gamepedia.com/Chunk_format"""

    def __init__(self, compound):
        super().__init__(dict(compound))

    def section(self, i: int) -> Optional[Section]:
        """Return a vertical section of the chunk, if available"""
        if self["DataVersion"] >= 2529:
            # https://minecraft.gamepedia.com/Java_Edition_20w17a
            return Section116(self["Level"]["Sections"][i + 1])
        if self["DataVersion"] >= 1631:
            return Section113(self["Level"]["Sections"][i + 1])
        else:
            raise ValueError("DataVersion {} not supported".format(self["DataVersion"]))

    def sections(self) -> Iterator[Section]:
        """Iterate all sections in the chunk"""
        for i in range(len(self["Level"]["Sections"]) - 1):
            section = self.section(i)
            if section:
                yield section

    def find_section(self, y: int) -> Optional[Section]:
        """Return the section with given y, if available"""
        return self.section(y >> 4)


class AnvilFile:
    """The Anvil file format
    is a storage format for Minecraft
    in which groups of 32×32 chunks are stored.

    A total of 512×256×512 blocks are stored.

    It's inizialized with only the chunk metadata,
    if a chunk is read, the whole file is parsed."""

    def __init__(self, filepath: Union[str, Path], byteorder="big") -> None:
        self.byteorder = byteorder
        self._filepath = Path(filepath)
        if not self._filepath.exists():
            raise ValueError("Path {} does not exists".format(filepath))
        if not self._filepath.is_file():
            raise ValueError("Path {} is not a file".format(filepath))
        self.__init_metadata()
        self.__chunks: Dict[Tuple[int, int], Optional[Chunk]] = {}

    def __str__(self) -> str:
        return "Anvil({!r})".format(self._filepath.name)

    def __repr__(self) -> str:
        return "Anvil('{}', {!r})".format(self._filepath.absolute(), self.byteorder)

    def __init_metadata(self) -> None:
        metadatas = {}
        with open(self._filepath.absolute(), "rb") as mcafile:
            offsets = []
            for i in range(1024):
                offsets.append(int.from_bytes(mcafile.read(3), self.byteorder))
                # sector_count = read_numeric(BYTE, mcafile, self.byteorder)
                mcafile.seek(1, 1)  # skip sector count
            for i in range(1024):
                x = i % 32
                z = i // 32
                metadatas[x, z] = _Metadata(offsets[i], read_numeric(INT, mcafile, self.byteorder))
        self._metadatas = metadatas

    def __read_chunks(self) -> None:
        if self.__chunks:
            return
        metadatas = sorted(self._metadatas.items(), key=lambda m: m[1].offset)
        with open(self._filepath.absolute(), "rb") as mcafile:
            for coord, metadata in metadatas:
                if not metadata.is_valid():
                    self.__chunks[coord] = None
                    continue
                mcafile.seek(metadata.seek)
                chunk_lenght = read_numeric(INT, mcafile, self.byteorder)
                compression = read_numeric(BYTE, mcafile, self.byteorder)
                if compression == 2:
                    data = zlib.decompress(mcafile.read(chunk_lenght - 1))
                else:
                    raise NotImplementedError("Compression = {}".format(compression))
                chunk_tag = Compound.parse(BytesIO(data), self.byteorder)
                self.__chunks[coord] = Chunk(chunk_tag[""])

    def chunk(self, x: int, z: int) -> Optional[Chunk]:
        """`x` and `z` refer to position within the region(AnvilFile)

        It returns a Chunks(Compound tag), if available (generated)"""
        if not self.__chunks:
            self.__read_chunks()
        return self.__chunks[x, z]

    def chunks(self) -> Iterator[Tuple[int, int, Chunk]]:
        """Iterate all available Chunks.

        It returns `x, z, chunk`. `x` and `z` are relative to the region(AnvinFile)"""
        for (x, z), metadata in self._metadatas.items():
            if metadata.is_valid():
                yield x, z, self.chunk(x, z)

    def find_chunk(self, x, z) -> Optional[Chunk]:
        """Given a block `x` and `z`, returns the chunk that contains the block."""
        return self.chunk(x >> 4 & 31, z >> 4 & 31)
