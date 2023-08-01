"""
Prints a map of maps.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from minenbt import SaveFolder

from .utils import dimension_player, get_world

SIZES = (128, 256, 512, 1024, 2048)


def _match_buckets(m: tuple[int, int], buckets: list[dict[tuple[int, int], str]], scale: int):
    f = []
    for i, b in enumerate(buckets):
        for bm in b.keys():
            dx = abs(bm[0] - m[0])
            dy = abs(bm[1] - m[1])
            if (dx == 0 and dy <= scale * 2) or (dx <= scale * 2 and dy == 0):
                f.append(i)
                break
    return f


def main(save_folder: "SaveFolder", dimension, scale: int) -> int:
    if not dimension:
        dimension = dimension_player(save_folder)
    world = get_world(save_folder, dimension)
    maps = [[] for _ in SIZES]  # type: list[list[tuple[str, tuple[int, int]]]]
    for id, mf in world.maps():
        if mf.compound["data"]["dimension"].py_str.split(":")[-1] != dimension:
            continue
        mscale = mf.compound["data"]["scale"].py_int
        maps[mscale].append(
            (id, (mf.compound["data"]["xCenter"].py_int, mf.compound["data"]["zCenter"].py_int))
        )
    pscale = list(range(0, len(SIZES)))
    ssep = "\n"
    if scale >= 0:
        pscale = [scale]
        ssep = ""
    for ascale in pscale:
        if not maps[ascale] and ascale != scale:
            continue
        size = SIZES[ascale]
        print(f"{ssep}Scale: {ascale} ({size}x{size})")
        # buckets is a list of nearby map
        # in one bucket there is a list of (x, z) -> id of map
        buckets = []  # type: list[dict[tuple[int, int], str]]
        for m in maps[ascale]:
            ok_buckets = _match_buckets(m[1], buckets, size)
            if not ok_buckets:
                # map too distant, create a new bucket
                buckets.append({m[1]: m[0]})
            else:
                # put the map in the best bucket
                buckets[ok_buckets[0]][m[1]] = m[0]
                # if there is more than one bucket available, merge in the first one
                for oldb_idx in sorted(ok_buckets[1:], reverse=True):
                    buckets[ok_buckets[0]].update(buckets.pop(oldb_idx))
        for i, bu in enumerate(buckets):
            print(f" Cluster {i+1}")
            ix = min(m[0] for m in bu.keys()) - size
            ax = max(m[0] for m in bu.keys()) + size
            iz = min(m[1] for m in bu.keys()) - size
            az = max(m[1] for m in bu.keys()) + size
            # header
            print("{:^9}".format("z/x"), end="")
            for z in range(iz, az + 1, size):
                print(f"{z:^9d}", end="")
            print("")
            # body
            for x in range(ix, ax + 1, size):
                print(f"{x:^9d}", end="")
                for z in range(iz, az + 1, size):
                    amap = bu.get((x, z), " ")
                    print(f"{amap[0]:^9}", end="")
                print("")

    return 0
