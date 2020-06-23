import datetime as dt
from pathlib import Path
from shutil import move
from sys import exit
from typing import Iterator, Optional, Tuple

from minenbt import Dimension, SaveFolder
from minenbt.utils import Coord, near_chunks
from nbtlib import Compound, File as ntbFile

__all__ = [
    "iterate_chunks",
    "get_world",
    "Center",
    "get_pos",
    "dimension_player",
    "pos_player",
    "get_player",
    "backup_write",
]


def Center(s: str) -> Coord:
    try:
        coords = [int(c.strip()) for c in s.split(",")]
    except ValueError:
        raise ValueError("Center should contains only numbers and commas")
    if len(coords) == 2:
        return Coord(coords[0], 0, coords[1])
    elif len(coords) == 3:
        return Coord(coords[0], coords[1], coords[2])
    else:
        raise ValueError("Center should be x,z or x,y,z")


def pos_player(save_folder: SaveFolder) -> Optional[Tuple[float, float, float]]:
    dat = save_folder.level_dat()
    if "Player" not in dat.root["Data"]:
        return None
    return dat.root["Data"]["Player"]["Pos"]


def dimension_player(save_folder: SaveFolder) -> Optional[str]:
    dat = save_folder.level_dat()
    if "Player" not in dat.root["Data"]:
        return None
    nbt_dimension = dat.root["Data"]["Player"]["Dimension"]
    if isinstance(nbt_dimension, int):
        # Until 1.15.2
        return {-1: "nether", 0: "overworld", 1: "end"}[nbt_dimension]
    # From 1.16
    return nbt_dimension.split(":")[1]


def iterate_chunks(
    world: Dimension, center: Optional[Tuple[int, int, int]], distance: Optional[int]
) -> Iterator[Tuple[Coord, Compound]]:
    if not distance or not center:
        for rx, rz, region in world.regions():
            for cx, cz, chunk in region.chunks():
                yield Coord.compose((rx, rz), (cx, cz)), chunk
    else:
        for coord in near_chunks(center[0], center[2], distance):
            try:
                chunk = world.region(*coord.region()).chunk(*coord.chunk())
                if chunk:
                    yield coord, chunk
            except KeyError:
                pass


def get_world(save_folder: SaveFolder, dimension: Optional[str]):
    """save folder + dimension name -> World"""
    if not dimension:
        dimension = dimension_player(save_folder)
        if dimension:
            print("Player found in {}".format(dimension.title()))
    if not dimension:
        print("Single player info not found, please specify --dimension")
        exit(99)
    return getattr(save_folder, dimension.lower())()


def get_pos(
    save_folder: SaveFolder, dimension: Optional[str], center=Optional[Coord]
) -> Optional[Tuple[int, int, int]]:
    if center:
        return center.x, center.y, center.x
    save_dimension = dimension_player(save_folder)
    if save_dimension and dimension and save_dimension != dimension:
        print("Center not provided, but provided dimension is different from player dimension")
        exit(97)
    pos = pos_player(save_folder)
    if not pos:
        return None
    print("Player at {:0.0f},{:0.0f},{:0.0f}".format(*pos))
    return (int(pos[0]), int(pos[1]), int(pos[2]))


def get_player(save_folder: SaveFolder, uuid: Optional[str]):
    """Get a player data.

    Return (level.dat file, playerdata file).  
    If uuid is None or uuid == Single player, return level.dat.  
    Else return playerdata file."""
    if not uuid:
        dat = save_folder.level_dat()
        if "Player" not in dat.root["Data"]:
            print("The Save is not for single player.")
            exit(96)
        return dat, None
    player = save_folder.player(uuid)
    if hasattr(player, "filename"):
        # ntblib.File, so from playerdata
        return None, player
    return save_folder.level_dat(), None


def backup_write(nbtfile: ntbFile):
    """Backup and save a ntblib.File."""
    path = Path(nbtfile.filename)
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    new_path = Path(str(path.absolute()) + "." + timestamp)
    move(path, new_path)
    nbtfile.save()
    return new_path
