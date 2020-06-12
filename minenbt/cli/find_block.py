"""
Find blocks by id (es: minecraft:diamond_ore).
"""
import minenbt
from minenbt.utils import Coord

from .utils import get_pos, get_world, iterate_chunks


def main(save_folder: minenbt.SaveFolder, dimension, center, distance, block_id) -> int:
    world = get_world(save_folder, dimension)
    pos = get_pos(save_folder, dimension, center)
    cpos = None
    if pos:
        cpos = Coord(*pos)
    if "minecraft:" not in block_id:
        block_id = "minecraft:" + block_id

    print("\nBlock founds:")
    for base_chunk, chunk in iterate_chunks(world, pos, distance):
        for section in chunk.sections():
            if block_id not in section.blocks_avaible():
                continue
            y = section["Y"] * 16
            for (bx, by, bz), block in section.blocks():
                sdist = ""
                c = Coord(base_chunk.x + bx, y + by, base_chunk.z + bz)
                if cpos:
                    sdist = " - {:.0f} blocks away".format(c.distance(cpos))
                if block_id == block["Name"]:
                    print("Found near {c}{}".format(sdist, c=c))
                    break
    return 0
