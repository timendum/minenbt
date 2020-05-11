"""Provides interfaces to handle specific Minecraft File"""
import zlib
from collections import namedtuple
from io import BytesIO
from pathlib import Path
from typing import Dict, Iterator, Optional, Tuple, Union

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
        self.__chunks: Dict[Tuple[int, int], Optional[Compound]] = {}

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
                    raise NotImplementedError(
                        "Compression = {}".format(compression)
                    )
                chunk_tag = Compound.parse(BytesIO(data), self.byteorder)
                chunk = chunk_tag[next(iter(chunk_tag), None)]
                self.__chunks[coord] = chunk

    def chunk(self, x: int, z: int) -> Optional[Compound]:
        """Chunks store the terrain and entities within a 16×256×16 area.

        `x` and `z` refer to position within the region(AnvilFile)

        It returns a Chunks(Compound tag), if available (generated)"""
        if not self.__chunks:
            self.__read_chunks()
        return self.__chunks[x, z]

    def chunks(self) -> Iterator[Tuple[int, int, Compound]]:
        """Iterate all available Chunks.

        It returns `x, z, chunk`. `x` and `z` are relative to the region(AnvinFile)"""
        for (x, z), metadata in self._metadatas.items():
            if metadata.is_valid():
                yield x, z, self.chunk(x, z)
