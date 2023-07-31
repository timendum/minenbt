import datetime as dt
import json
from pathlib import Path
from shutil import move
from sys import exit
from typing import TYPE_CHECKING

from amulet_nbt import AbstractBaseTag
from numpy import ndarray

from minenbt.file_formats import NbtFile
from minenbt.utils import Coord, near_chunks, parse_uuid

if TYPE_CHECKING:
    from collections.abc import Iterator

    from amulet_nbt import CompoundTag

    from minenbt import AnvilFolder, Chunk, Dimension, SaveFolder

__all__ = [
    "iterate_chunks",
    "get_world",
    "center",
    "get_pos",
    "dimension_player",
    "pos_player",
    "get_player_file",
    "find_player",
    "backup_save",
    "json_print",
    "json_pprint"
]


def center(s: str) -> Coord:
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


def pos_player(save_folder: "SaveFolder") -> tuple[float, float, float] | None:
    dat = save_folder.level_dat()
    if "Player" not in dat.compound["Data"]:
        return None
    return [t.py_float for t in dat.compound["Data"]["Player"]["Pos"].py_list]


def dimension_player(save_folder: "SaveFolder") -> str | None:
    dat = save_folder.level_dat()
    if "Player" not in dat.compound["Data"]:
        return None
    nbt_dimension = dat.compound["Data"]["Player"]["Dimension"]
    return nbt_dimension.py_str.split(":")[1]


def iterate_chunks(
    world: "AnvilFolder", center: tuple[int, int, int] | None, distance: int | None
) -> "Iterator[tuple[Coord, Chunk]]":
    chunk = None  # type: None | Chunk
    if not distance or not center:
        for rx, rz, region in world.all():
            for cx, cz, chunk in region.chunks():
                yield Coord.compose((rx, rz), (cx, cz)), chunk
    else:
        for coord in near_chunks(center[0], center[2], distance):
            try:
                chunk = world.single(*coord.region()).chunk(*coord.chunk())
                if chunk:
                    yield coord, chunk
            except KeyError:
                pass


    """save folder + dimension name -> World"""
def get_world(save_folder: "SaveFolder", dimension: str | None) -> "Dimension":
    if not dimension:
        dimension = dimension_player(save_folder)
        if dimension:
            print(f"Player found in {dimension.title()}")
    if not dimension:
        print("Single player info not found, please specify --dimension")
        exit(99)
    return getattr(save_folder, dimension.lower())()


def get_pos(
    save_folder: "SaveFolder", dimension: str | None, center=Coord | None
) -> tuple[int, int, int] | None:
    if center:
        return center
    save_dimension = dimension_player(save_folder)
    if save_dimension and dimension and save_dimension != dimension:
        return None
    pos = pos_player(save_folder)
    if not pos:
        return None
    print("Player at {:0.0f},{:0.0f},{:0.0f}".format(*pos))
    return (int(pos[0]), int(pos[1]), int(pos[2]))


def get_player_file(
    save_folder: "SaveFolder", uuid: str | None
) -> "tuple[NbtFile | None, NbtFile | None]":
    """Get a player data.

    Return (level.dat file, playerdata file).
    If uuid is None or uuid == Single player, return level.dat.
    Else return playerdata file."""
    dat = save_folder.level_dat()
    if not uuid:
        if "Player" not in dat.compound["Data"]:
            print("The Save is not for single player.")
            exit(96)
        return dat, None
    try:
        sp_uuid = parse_uuid(dat.compound["Data"]["Player"], "UUID")
        if uuid == str(sp_uuid):
            return dat, None
    except:
        pass
    return None, NbtFile(save_folder._folder / "playerdata" / f"{uuid}.dat")


def find_player(level_dat: "None | NbtFile", playerdata: "None | NbtFile") -> "CompoundTag":
    if level_dat:
        return level_dat.compound["Data"]["Player"]
    if playerdata:
        return playerdata.compound
    raise ValueError("No valid player found")


def backup_save(level_dat: "None | NbtFile", playerdata: "None | NbtFile") -> Path:
    """Backup and save a ntblib.File."""
    nbtfile = level_dat or playerdata
    if not nbtfile:
        raise ValueError("No valid file")
    path = Path(nbtfile.filename)
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
    new_path = Path(str(path.absolute()) + "." + timestamp)
    move(path, new_path)
    nbtfile.save()
    return new_path


def plain_print(o: "CompoundTag"):
    if o:
        print(o.to_snbt())


def ident_print(o: "CompoundTag"):
    if o:
        print(o.to_snbt(indent=2))


class NbtJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, AbstractBaseTag):
            for p in ("py_dict", "py_list", "py_int", "py_float", "py_str", "np_array"):
                try:
                    return getattr(o, p)
                except AttributeError:
                    pass
        if isinstance(o, ndarray):
            return o.tolist()
        return json.JSONEncoder.default(self, o)


def json_print(o):
    return print(json.dumps(o, cls=NbtJSONEncoder))

def json_pprint(o):
    return print(json.dumps(o, cls=NbtJSONEncoder,indent="  "))
