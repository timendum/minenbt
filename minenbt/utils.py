import bisect
from math import floor, pow as mpow, sqrt
from typing import List, NamedTuple, Tuple

__all__ = ["Coord", "near_regions", "near_chunks"]


class Coord(NamedTuple):
    x: int
    y: int
    z: int

    def region(self) -> Tuple[int, int]:
        return self.x >> 9, self.z >> 9

    def chunk(self) -> Tuple[int, int]:
        return self.x >> 4 & 31, self.z >> 4 & 31

    def section(self) -> int:
        return self.y >> 4

    def block(self) -> Tuple[int, int, int]:
        return self.x & 15, self.y & 15, self.z & 15

    @classmethod
    def compose(cls, region=[0, 0], chunk=[0, 0], section=0, block=[0, 0, 0]) -> "Coord":
        x = (region[0] << 9) + (chunk[0] << 4) + block[0]
        y = (section << 4) + block[1]
        z = (region[1] << 9) + (chunk[1] << 4) + block[2]
        return cls(x, y, z)

    def distance(self, c: "Coord") -> float:
        return sqrt(mpow(self.x - c.x, 2) + mpow(self.y - c.y, 2) + mpow(self.z - c.z, 2))

    def __str__(self):
        return "({self.x}, {self.y}, {self.z})".format(self=self)


def near_regions(x, z, distance) -> List[Tuple[int, int]]:
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


def near_chunks(x, z, distance) -> List[Coord]:
    """Return an list of Coord, from nearest to farthest, one Coord for every chunck.
    Every returned Coord has a distance from `(x,z)` lesser than `distance`."""
    start = Coord(x, 0, z)
    block_delta = start.block()
    results = []
    region_range = floor(distance / 512) + 1
    for rx in range(-region_range, region_range + 1):
        for rz in range(-region_range, region_range + 1):
            for cx in range(0, 32):
                for cz in range(0, 32):
                    point = Coord.compose((rx, rz), (cx, cz), 0, block_delta)
                    results.append((point, start.distance(point)))
    results = sorted(results, key=lambda k: k[1])
    results = results[: bisect.bisect_right([r[1] for r in results], distance)]
    return [r[0] for r in results]
