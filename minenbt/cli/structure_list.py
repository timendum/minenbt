"""
Prints all structures in the Overworld
"""
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import minenbt

from .utils import get_pos, get_world, iterate_chunks


def main(save_folder: "minenbt.SaveFolder", dimension, center, distance) -> int:
    world = get_world(save_folder, dimension)
    pos = get_pos(save_folder, dimension, center)
    seen: dict[str, list[tuple[int, int]]] = {}

    def print_if_new(name: str, x: int, y, z: int) -> None:
        name = name.split(":")[-1]
        name = name.replace("_", " ").title()
        if name not in seen:
            seen[name] = []
        for s in seen[name]:
            if math.sqrt((s[0] - x) ** 2 + (s[1] - z) ** 2) < 32:
                break
        else:
            print(f"{name} at ({x}, {y}, {z})")
        seen[name].append((x, z))

    print("Structures:\n")
    for base_chunk, chunk in iterate_chunks(world.regions, pos, distance):
        for k, v in chunk["structures"]["References"].items():
            if not len(v):
                continue
            x = v[0] % 32
            z = v[0] >> 32
            print_if_new(k, base_chunk.x + x, "?", base_chunk.z + z)
        for k, v in chunk["structures"]["starts"].items():
            if v["id"].py_str == "INVALID":
                continue
            x, y, z = v["Children"][0]["BB"].np_array.tolist()[0:3]
            # x = int((bb[0] + bb[3]) / 2)
            # y = int((bb[1] + bb[4]) / 2)
            # z = int((bb[2] + bb[5]) / 2)
            print_if_new(k, x, y, z)
    return 0
