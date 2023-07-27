"""
Dump a minecraft location.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from minenbt import SaveFolder

from .utils import get_pos, get_world, json_pprint, json_print


def main(save_folder: "SaveFolder", dimension, center, ltype, pretty_print) -> int:
    world = get_world(save_folder, dimension)
    pos = get_pos(save_folder, dimension, center)
    if not pos:
        print("Position not provided")
        exit(97)

    pprint = json_print
    if pretty_print:
        pprint = json_pprint

    region = world.regions.find(pos[0], pos[2])
    chunk = region.find_chunk(pos[0], pos[2])
    if ltype == "chunk" or not chunk:
        pprint(chunk)
        return 0
    sector = chunk.find_section(pos[1])
    if ltype == "sector" or not sector:
        pprint(sector)
        return 0
    block = sector.find_block(pos[0], pos[1], pos[2])
    if ltype == "block" or not block:
        pprint(block)
        return 0
    return -1
