"""
Prints all mobs in the Overworld (Entities with Brain)
"""

from typing import TYPE_CHECKING


if TYPE_CHECKING:

    from minenbt import SaveFolder
from minenbt.utils import Coord

from .utils import get_pos, get_world, iterate_chunks


def main(save_folder: "SaveFolder", dimension, center, distance) -> int:
    world = get_world(save_folder, dimension)
    pos = get_pos(save_folder, dimension, center)
    if pos:
        cpos = Coord(*pos)
    print("\nEntities:")
    for _, chunk in iterate_chunks(world.entities, pos, distance):
        for e in chunk.get("Entities", ()):
            # Filter mobs
            if "Brain" in e:
                sdist = ""
                c = Coord(*[int(v.py_float) for v in e["Pos"].py_list])
                if cpos:
                    sdist = f" - {c.distance(cpos):.0f} blocks away"
                print(
                    "{:s} at ({}){}".format(
                        e["id"].py_str.replace("minecraft:", "").replace("_", " ").title(),
                        c,
                        sdist,
                    )
                )
    return 0
