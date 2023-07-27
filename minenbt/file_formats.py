"""Provides interfaces to handle specific Minecraft File"""
import zlib
from collections import namedtuple
from math import ceil
from pathlib import Path
from typing import TYPE_CHECKING

import amulet_nbt

if TYPE_CHECKING:
    from collections.abc import Iterator
    from io import BufferedReader

    from amulet_nbt._dtype import AnyNBT

import numpy
from amulet_nbt import CompoundTag
from amulet_nbt import load as load_nbt

__all__ = ["AnvilFile", "NbtFile", "Chunk"]


class NbtFile:
    def __init__(self, filename: "Path | str") -> None:
        self.filename = str(filename)
        self.tag = load_nbt(self.filename)

    def save(self) -> None:
        self.tag.save_to(self.filename)


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


class Section(CompoundTag):
    """A 16×16×16 section of the chuck for DataVersion < 2529."""

    def __init__(self, compound) -> None:
        super().__init__(dict(compound))
        self._states: numpy.array | None = None
        self._palette: tuple[str] | None = None
        if (
            "block_states" not in self
            or "palette" not in self["block_states"]
            or "data" not in self["block_states"]
        ):
            return
        self._palette = tuple(p["Name"].py_str for p in self["block_states"]["palette"])
        nbit = max((len(self._palette) - 1).bit_length(), 4)
        if len(self["block_states"]["data"]) != ceil(16 * 16 * 16 / (64 // nbit)):
            raise ValueError(
                "There are {} 64-bit fields but {} states".format(
                    len(self["block_states"]["data"]), len(self._palette)
                )
            )
        unused = 64 % nbit
        blength = 64 - unused
        mask = pow(2, nbit) - 1
        states = []
        for longstate in self["block_states"]["data"].np_array:
            for _i in range(0, blength, nbit):
                states.append(longstate & mask)
                longstate = longstate >> nbit
        self._states = numpy.reshape(states[: 16 * 16 * 16], [16, 16, 16]).tolist()

    def block(self, x, y, z) -> str | None:
        if not self._palette or self._states is None:
            return None
        return self._palette[self._states[y][z][x]]

    def blocks(self) -> "Iterator[tuple[tuple[int, int, int], str]]":
        if self._palette:
            for (y, z, x), state in numpy.ndenumerate(self._states):
                yield (x, y, z), self._palette[state]

    def blocks_available(self) -> set[str]:
        if not self._palette:
            return set()
        return set([n for n in self._palette])

    def find_block(self, x, y, z) -> str | None:
        if not self._palette or self._states is None:
            return None
        x = x & 15
        y = y & 15
        z = z & 15
        return self._palette[self._states[y][z][x]]

    @property
    def py_dict(self) -> "dict[str, AnyNBT | dict[str, str]]":
        return {
            "blocks": {",".join(str(i) for i in c): b for c, b in self.blocks()}
        } | super().py_dict


class Chunk(CompoundTag):
    """Chunks store the terrain and entities within a 16×384×16 area.

    https://minecraft.gamepedia.com/Chunk_format"""

    def section(self, i: int) -> Section | None:
        """Return a vertical section of the chunk, if available"""
        if self["DataVersion"].py_int >= 2529:
            # https://minecraft.gamepedia.com/Java_Edition_20w17a
            return Section(self["sections"][i + 1])
        raise ValueError("DataVersion {} not supported".format(self["DataVersion"]))

    def sections(self) -> "Iterator[Section]":
        """Iterate all sections in the chunk"""
        for i in range(len(self["sections"]) - 1):
            section = self.section(i)
            if section:
                yield section

    def find_section(self, y: int) -> Section | None:
        """Return the section with given y, if available"""
        return self.section((y >> 4) + 3)


class AnvilFile:
    """The Anvil file format
    is a storage format for Minecraft
    in which groups of 32×32 chunks are stored.

    It's inizialized with only the chunk metadata,
    if a chunk is read, the whole file is parsed."""

    def __init__(self, filepath: str | Path, byteorder="big") -> None:
        self.byteorder = byteorder
        self._filepath = Path(filepath)
        if not self._filepath.exists():
            raise ValueError(f"Path {filepath} does not exists")
        if not self._filepath.is_file():
            raise ValueError(f"Path {filepath} is not a file")
        self.__init_metadata()
        self.__chunks: dict[tuple[int, int], Chunk | None] = {}

    def __str__(self) -> str:
        return f"Anvil({self._filepath.name!r})"

    def __repr__(self) -> str:
        return f"Anvil('{self._filepath.absolute()}', {self.byteorder!r})"

    def __read_int_from_bytes(self, mcafile: "BufferedReader", size):
        return int.from_bytes(mcafile.read(size), self.byteorder)

    def __init_metadata(self) -> None:
        metadatas = {}
        with open(self._filepath.absolute(), "rb") as mcafile:
            offsets = []
            for _i in range(1024):
                offsets.append(self.__read_int_from_bytes(mcafile, 3))
                # sector_count = read_numeric(BYTE, mcafile, self.byteorder)
                mcafile.seek(1, 1)  # skip sector count
            for i in range(1024):
                x = i % 32
                z = i // 32
                metadatas[x, z] = _Metadata(offsets[i], self.__read_int_from_bytes(mcafile, 4))
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
                chunk_lenght = self.__read_int_from_bytes(mcafile, 4)
                compression = mcafile.read(1)[0]
                if compression == 2:
                    data = zlib.decompress(mcafile.read(chunk_lenght - 1))
                else:
                    raise NotImplementedError(f"Compression = {compression}")
                chunk_tag = amulet_nbt.load(data, little_endian=(self.byteorder == "little"))
                self.__chunks[coord] = Chunk(chunk_tag.compound)

    def chunk(self, x: int, z: int) -> Chunk | None:
        """`x` and `z` refer to position within the region(AnvilFile)

        It returns a Chunks(Compound tag), if available (generated)"""
        if not self.__chunks:
            self.__read_chunks()
        return self.__chunks[x, z]

    def chunks(self) -> "Iterator[tuple[int, int, Chunk]]":
        """Iterate all available Chunks.

        It returns `x, z, chunk`. `x` and `z` are relative to the region(AnvinFile)"""
        for (x, z), metadata in self._metadatas.items():
            if metadata.is_valid():
                yield x, z, self.chunk(x, z)

    def find_chunk(self, x, z) -> Chunk | None:
        """Given a block `x` and `z`, returns the chunk that contains the block."""
        return self.chunk(x >> 4 & 31, z >> 4 & 31)
