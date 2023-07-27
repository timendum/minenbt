import bisect
from math import floor, sqrt
from math import pow as mpow
from typing import NamedTuple
from uuid import UUID

import numpy as np
from amulet_nbt import CompoundTag, IntArrayTag

__all__ = ["Coord", "near_regions", "near_chunks", "parse_uuid"]


class Coord(NamedTuple):
    x: int
    y: int
    z: int

    def region(self) -> tuple[int, int]:
        return self.x >> 9, self.z >> 9

    def chunk(self) -> tuple[int, int]:
        return self.x >> 4 & 31, self.z >> 4 & 31

    def section(self) -> int:
        return self.y >> 4

    def block(self) -> tuple[int, int, int]:
        return self.x & 15, self.y & 15, self.z & 15

    @classmethod
    def compose(cls, region=(0, 0), chunk=(0, 0), section=0, block=(0, 0, 0)) -> "Coord":
        x = (region[0] << 9) + (chunk[0] << 4) + block[0]
        y = (section << 4) + block[1]
        z = (region[1] << 9) + (chunk[1] << 4) + block[2]
        return cls(x, y, z)

    def distance(self, c: "Coord") -> float:
        return sqrt(mpow(self.x - c.x, 2) + mpow(self.y - c.y, 2) + mpow(self.z - c.z, 2))

    def __str__(self):
        return "({self.x}, {self.y}, {self.z})".format(self=self)


def near_regions(x, z, distance) -> list[tuple[int, int]]:
    """Returns a list of (region x, region z) of region
    in a square of side distance*2
    centered on (x, z).

    You can pass the returned values to `minenbt.Dimension.region`"""
    c = Coord(x, 0, z)
    center_region = c.region()
    regions = [center_region]
    cp = Coord(x + distance, 0, z + distance).region()
    cm = Coord(x - distance, 0, z - distance).region()
    for dx in range(cm[0], cp[0] + 1):
        for dy in range(cm[1], c[1] + 1):
            regions.append((center_region[0] + dx, center_region[1] + dy))
    return regions


def near_chunks(x, z, distance) -> list[Coord]:
    """Return an list of Coord, from nearest to farthest, one Coord for every chunck.
    Every returned Coord has a distance from `(x,z)` lesser than `distance`."""
    start = Coord(x, 0, z)
    srx, srz = start.region()
    results = []
    xregion_range = floor(distance / 512)
    zregion_range = xregion_range
    # distance from borders
    dx = x % 512
    if min(abs(dx - 512), dx) < distance % 512:
        xregion_range += 1
    dz = z % 512
    if min(abs(dz - 512), dz) < distance % 512:
        zregion_range += 1
    # iterate every regions in range
    for rx in range(-xregion_range, xregion_range + 1):
        for rz in range(-zregion_range, zregion_range + 1):
            # iterate every chunk in regions
            for cx in range(0, 33):
                for cz in range(0, 33):
                    point = Coord.compose((rx + srx, rz + srz), (cx, cz), 0)
                    results.append((point, start.distance(point)))
    results = sorted(results, key=lambda k: k[1])
    nbisect = bisect.bisect_right([r[1] for r in results], distance)
    results = results[:nbisect]
    return [r[0] for r in results]


def parse_uuid(compound: CompoundTag, prefix="UUID") -> UUID:
    """Return an uuid.UUID from a compund tag.

    See https://minecraft.gamepedia.com/UUID"""
    # From MC 1.16
    ints = compound[prefix]
    if not isinstance(ints, IntArrayTag):
        raise ValueError("Incorrect tag")
    # convert so unsigned
    uints = [np.int32(i).astype(np.uint32).item() for i in ints.np_array]
    # build 128 bit integer
    return UUID(int=(uints[0] << 96) + (uints[1] << 64) + (uints[2] << 32) + uints[3])
