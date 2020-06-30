"""
Dump a minecraft location.
"""

import json

import minenbt

import nbtlib

from .utils import get_pos, get_world


class CustomJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ensure_ascii = False

    def default(self, o):
        if isinstance(o, nbtlib.Array):
            return "[" + ", ".join([self.encode(i) for i in o]) + "]"
        super().default(o)


def main(save_folder: minenbt.SaveFolder, dimension, center, ltype, pretty_print) -> int:
    world = get_world(save_folder, dimension)
    pos = get_pos(save_folder, dimension, center)
    if not pos:
        print("Position not provided")
        exit(97)
    encoder = CustomJSONEncoder()

    def pprint(o):
        print(encoder.encode(o))

    if pretty_print:
        encoder.indent = 4
    region = world.find_region(pos[0], pos[2])
    if ltype == "region" or not region:
        pprint(region)
        return 0
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
