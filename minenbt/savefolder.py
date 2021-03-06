from functools import lru_cache
from pathlib import Path
from typing import Iterable, Tuple, Union

import nbtlib

from . import AnvilFile
from .utils import parse_uuid

__all__ = ["SaveFolder", "Dimension"]


class Dimension:
    """A Dimension (folder) in Minecraft"""

    def __init__(self, folder: Union[str, Path]) -> None:
        self._folder = Path(folder)
        if not self._folder.exists():
            raise ValueError("Path {} does not exists".format(folder))
        if not self._folder.is_dir():
            raise ValueError("Path {} is not a folder".format(folder))
        self.__init_region_files()
        self.__init_poi_files()

    def __init_region_files(self) -> None:
        region_files = {}
        for mcafile in (self._folder / "region").glob("r.*.mca"):
            _, sx, sz, _ = mcafile.name.split(".")
            region_files[int(sx), int(sz)] = mcafile
        self._region_files = region_files

    @lru_cache(maxsize=16)
    def region(self, x: int, z: int) -> AnvilFile:
        """Return the region as an AnvilFile.

        `x` and `z` refer to position expressed in the filename."""
        return AnvilFile(self._region_files[x, z].absolute())

    def regions(self) -> Iterable[Tuple[int, int, AnvilFile]]:
        """Iterate all available Regions(AnvilFiles).

        It returns `x, z, region`. `x` and `z` are expressed in the filename."""
        for x, z in self._region_files.keys():
            yield x, z, self.region(x, z)

    def __init_poi_files(self) -> None:
        poi_files = {}
        for mcafile in (self._folder / "poi").glob("r.*.mca"):
            _, sx, sz, _ = mcafile.name.split(".")
            poi_files[int(sx), int(sz)] = mcafile
        self._poi_files = poi_files

    def poi(self, x, z) -> AnvilFile:
        """Return the Point of interest as an AnvilFile.

        `x` and `z` refer to position expressed in the filename."""
        return AnvilFile(self._poi_files[x, z].absolute())

    def pois(self) -> Iterable[Tuple[int, int, AnvilFile]]:
        """Iterate all available POIs(AnvilFiles).

        It returns `x, z, region`. `x` and `z` are expressed in the filename."""
        for x, z in self._poi_files.keys():
            yield x, z, self.poi(x, z)

    def raid(self) -> AnvilFile:
        """Return raid information as an AnvilFile."""
        for mcafile in (self._folder / "data").glob("raid*.dat"):
            return nbtlib.load(mcafile.absolute())
        raise IOError("Raid file not found")

    def regions_xzs(self) -> Iterable[Tuple[int, int]]:
        """Iterate all regions, return x, z for that region."""
        for x, z in self._region_files.keys():
            yield x, z

    def find_region(self, x: int, z: int) -> AnvilFile:
        """Given a block `x` and `z`, returns the region that contains the block."""
        return self.region(x >> 9, z >> 9)

    def find_chunk(self, x: int, z: int) -> nbtlib.Compound:
        """Given a block `x` and `z`, returns the chunk that contains the block."""
        return self.region(x >> 9, z >> 9).chunk(x >> 4 & 31, z >> 4 & 31)

    def __repr__(self) -> str:
        return "Dimension('{}')".format(self._folder.absolute())


class SaveFolder:
    """A Minecraft Save Folder"""

    # https://minecraft.gamepedia.com/Java_Edition_level_format

    def __init__(self, folder: Union[str, Path]) -> None:
        self._folder = Path(folder)
        if not self._folder.exists():
            raise ValueError("Path {} does not exists".format(folder))
        if not self._folder.is_dir():
            raise ValueError("Path {} is not a folder".format(folder))
        self.__level_dat = None

    def level_dat(self) -> nbtlib.File:
        """Returns the leve.dat file as a NBT Compound tag."""
        if not self.__level_dat:
            self.__level_dat = nbtlib.load(self._folder / "level.dat")
        return self.__level_dat

    def __str__(self) -> str:
        return "SaveFolder({})".format(self.level_dat().root["Data"]["LevelName"])

    def __repr__(self) -> str:
        return "SaveFolder('{}')".format(self._folder.absolute())

    def overworld(self) -> Dimension:
        """Return the Overworld dimension."""
        return Dimension(self._folder.absolute())

    def the_nether(self) -> Dimension:
        """Return the Nether dimension."""
        return Dimension((self._folder / "DIM-1").absolute())

    def the_end(self) -> Dimension:
        """Return the End dimension."""
        return Dimension((self._folder / "DIM1").absolute())

    def players(self) -> Iterable[str]:
        """Return a list of player's UUIDs."""
        return [p.stem for p in (self._folder / "playerdata").glob("*.dat")]

    def player(self, uuid: str) -> nbtlib.Compound:
        """Load a player from `level.dat` or `playerdata` folder."""
        dat = self.level_dat()
        sp_uuid = None
        if "Player" in dat.root["Data"]:
            sp_data = dat.root["Data"]["Player"]
            sp_uuid = parse_uuid(sp_data, "UUID")
        if uuid == str(sp_uuid):
            return dat.root["Data"]["Player"]
        return nbtlib.load(self._folder / "playerdata" / "{}.dat".format(uuid))
