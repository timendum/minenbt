"""
Dump a minecraft location.
"""

import minenbt

from .utils import get_pos, get_world


def main(save_folder: minenbt.SaveFolder, dimension, center, ltype) -> int:
    world = get_world(save_folder, dimension)
    pos = get_pos(save_folder, dimension, center)
    if not pos:
        print("Position not provided")
        exit(97)
    region = world.find_region(pos[0], pos[2])
    if ltype == "region" or not region:
        print("Region:" + repr(region))
        return 0
    chunk = region.find_chunk(pos[0], pos[2])
    if ltype == "chunk" or not chunk:
        print("Chunk:" + repr(chunk))
        return 0
    sector = chunk.find_section(pos[1])
    if ltype == "sector" or not sector:
        print("Sector:" + repr(chunk))
        return 0
    block = sector.find_block(pos[0], pos[1], pos[2])
    if ltype == "block" or not block:
        print("Block:" + repr(block))
        return 0
    return -1
