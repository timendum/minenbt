"""
Find slime chunks.
"""
from typing import TYPE_CHECKING

from minenbt.utils import Coord

if TYPE_CHECKING:
    import minenbt

from .utils import get_pos, get_world, iterate_chunks


def check_chunk(seed, x, z):
    rseed = seed + x * z * 0x4C1906 + x * 0x5AC0DB + z * z * 0x4307A7 + (z * 0x5F24F) ^ 0x3AD8025F
    multiplier = 0x5DEECE66D
    mask = (1 << 48) - 1
    # scrable input seed
    _seed = (rseed ^ multiplier) & mask

    # generate a 31 bit integer
    def _next():
        nonlocal _seed
        # generate next seed
        while True:
            oldseed = _seed
            nextseed = (oldseed * multiplier + 0xB) & mask
            if oldseed != nextseed:
                break
        _seed = nextseed
        nr = nextseed >> 17
        # convert nr to java integer
        if nr & (1 << 31):
            nr -= 1 << 32
        return nr

    # generate 0-9 random
    r = _next()
    u = r
    r = u % 10
    while u - r + 9 < 0:
        u = _next()
        r = u % 10
    return r == 0


def main(save_folder: "minenbt.SaveFolder", dimension, center, distance) -> int:
    world = get_world(save_folder, dimension)
    pos = get_pos(save_folder, dimension, center)
    data = save_folder.level_dat().compound["Data"]
    seed = data["WorldGenSettings"]["seed"]
    cpos = None
    if pos:
        cpos = Coord(x=pos[0], y=0, z=pos[2])

    print("\nChunks founds:")
    for base_chunk, _ in iterate_chunks(world.regions, pos, distance):
        if check_chunk(seed, base_chunk.x // 16, base_chunk.z // 16):
            sdist = ""
            if cpos:
                sdist = f" - {base_chunk.distance(cpos):.0f} blocks away"
            c = {
                "xa": base_chunk.x - base_chunk.block()[0],
                "za": base_chunk.z - base_chunk.block()[1],
            }
            c["xb"] = c["xa"] + 15
            c["zb"] = c["za"] + 15
            print("Found between {xa},{za} and {xb},{zb}{}".format(sdist, **c))
    return 0
