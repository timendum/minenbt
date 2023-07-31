from pathlib import Path
from typing import TYPE_CHECKING

from minenbt.file_formats import NbtFile

if TYPE_CHECKING:
    from collections.abc import Iterable

from amulet_nbt import CompoundTag, StringTag

from . import AnvilFile
from .utils import parse_uuid

__all__ = ["SaveFolder", "Dimension", "AnvilFolder"]


class AnvilFolder:
    def __init__(self, files: dict[tuple[int, int], Path]) -> None:
        self._files = files
        self._anvils = {}  # type: dict[tuple[int, int], AnvilFile]

    def single(self, x: int, z: int) -> AnvilFile:
        if (x, z) not in self._anvils:
            self._anvils[x, z] = AnvilFile(self._files[x, z])
        return self._anvils[x, z]

    def all(self) -> "Iterable[tuple[int, int, AnvilFile]]":
        """Iterate all available Regions(AnvilFiles).

        It returns `x, z, region`. `x` and `z` are expressed in the filename."""
        for x, z in self._files.keys():
            yield x, z, self.single(x, z)

    def xzs(self) -> "Iterable[tuple[int, int]]":
        """Iterate all regions, return x, z for that region."""
        yield from self._files.keys()

    def find(self, x: int, z: int) -> AnvilFile:
        """Given a block `x` and `z`, returns the region that contains the block."""
        return self.single(x >> 9, z >> 9)

    def find_chunk(self, x: int, z: int) -> CompoundTag:
        """Given a block `x` and `z`, returns the chunk that contains the block."""
        return self.single(x >> 9, z >> 9).chunk(x >> 4 & 31, z >> 4 & 31)

    @staticmethod
    def from_folder(base_folder: "Path", folder_name: str, filter="r.*.mca") -> "AnvilFolder":
        entity_files = {}
        for mcafile in (base_folder / folder_name).glob("r.*.mca"):
            _, sx, sz, _ = mcafile.name.split(".")
            entity_files[int(sx), int(sz)] = mcafile
        return AnvilFolder(entity_files)


class Dimension:
    """A Dimension (folder) in Minecraft"""

    def __init__(self, folder: str | Path) -> None:
        self._folder = Path(folder)
        if not self._folder.exists():
            raise ValueError(f"Path {folder} does not exists")
        if not self._folder.is_dir():
            raise ValueError(f"Path {folder} is not a folder")
        self.regions = AnvilFolder.from_folder(self._folder, "region")
        self.entities = AnvilFolder.from_folder(self._folder, "entities")
        self.pois = AnvilFolder.from_folder(self._folder, "poi")

    def raid(self) -> "Iterable[NbtFile]":
        """Return raid information as an NbtFile."""
        for mcafile in (self._folder / "data").glob("raid*.dat"):
            yield NbtFile(mcafile.absolute())

    def maps(self) -> "Iterable[NbtFile]":
        """Return all maps as `NbtFile`."""
        for mcafile in (self._folder / "data").glob("map_*.dat"):
            yield NbtFile(mcafile.absolute())

    def map(self, id: str) -> NbtFile | None:
        """Return a specific map by id."""
        mcafile= self._folder / "data" / ("map_" + id + ".dat")
        if mcafile.is_file():
            return NbtFile(mcafile.absolute())
        return None

    def __repr__(self) -> str:
        return f"Dimension('{self._folder.absolute()}')"


class SaveFolder:
    """A Minecraft Save Folder"""

    # https://minecraft.fandom.com/Java_Edition_level_format

    def __init__(self, folder: str | Path) -> None:
        self._folder = Path(folder)
        if not self._folder.exists():
            raise ValueError(f"Path {folder} does not exists")
        if not self._folder.is_dir():
            raise ValueError(f"Path {folder} is not a folder")
        self.__level_dat: NbtFile | None = None
        self.__overworld: Dimension | None = None
        self.__the_nether: Dimension | None = None
        self.__the_end: Dimension | None = None

    def level_dat(self) -> NbtFile:
        """Returns the leve.dat file as a NBT Compound tag."""
        if not self.__level_dat:
            self.__level_dat = NbtFile(self._folder / "level.dat")
        return self.__level_dat

    def __str__(self) -> str:
        data = self.level_dat().compound["Data"]
        if isinstance(data, CompoundTag):
            value = data["LevelName"]
            if isinstance(value, StringTag):
                return f"SaveFolder({value.py_str})"
        raise ValueError("Level.dat corrupted")

    def __repr__(self) -> str:
        return f"SaveFolder('{self._folder.absolute()}')"

    def overworld(self) -> Dimension:
        """Return the Overworld dimension."""
        if not self.__overworld:
            self.__overworld = Dimension(self._folder.absolute())
        return self.__overworld

    def the_nether(self) -> Dimension:
        """Return the Nether dimension."""
        if not self.__the_nether:
            self.__the_nether = Dimension((self._folder / "DIM-1").absolute())
        return self.__the_nether

    def the_end(self) -> Dimension:
        """Return the End dimension."""
        if not self.__the_end:
            self.__the_end = Dimension((self._folder / "DIM1").absolute())
        return self.__the_end

    def players(self) -> "Iterable[str]":
        """Return a list of player's UUIDs."""
        return [p.stem for p in (self._folder / "playerdata").glob("*.dat")]

    def player(self, uuid: str) -> NbtFile | CompoundTag:
        """Load a player from `level.dat` or `playerdata` folder."""
        dat = self.level_dat()
        sp_uuid = None
        if (
            dat.compound["Data"]
            and isinstance(dat.compound["Data"], CompoundTag)
            and "Player" in dat.compound["Data"]
            and isinstance(dat.compound["Data"], CompoundTag)
        ):
            sp_data = dat.compound["Data"]["Player"]
            if isinstance(sp_data, CompoundTag):
                sp_uuid = parse_uuid(sp_data, "UUID")
                if uuid == str(sp_uuid):
                    return sp_data
        return NbtFile(self._folder / "playerdata" / f"{uuid}.dat")
