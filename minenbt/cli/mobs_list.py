"""
Prints all mobs in the Overworld (Entities with Brain)
"""

import minenbt
from minenbt.utils import Coord

from .utils import get_pos, get_world, iterate_chunks


def main(save_folder: minenbt.SaveFolder, dimension, center, distance) -> int:
    world = get_world(save_folder, dimension)
    pos = get_pos(save_folder, dimension, center)
    if pos:
        cpos = Coord(*pos)
    print("\nEntities:")
    for _, chunk in iterate_chunks(world, pos, distance):
        for e in chunk["Level"].get("Entities"):
            # Filter mobs
            if "Brain" in e:
                sdist = ""
                if cpos:
                    c = Coord(*e["Pos"])
                    sdist = " - {:.0f} blocks away".format(c.distance(cpos))
                print(
                    "{:s} at ({:0.0f}, {:0.0f}, {:0.0f}){}".format(
                        e["id"].replace("minecraft:", "").replace("_", " ").title(),
                        *e["Pos"],
                        sdist
                    )
                )
    return 0
