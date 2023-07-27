"""
Prints all containers (chest, barrel, minecart with chest).
"""
from collections import Counter

from amulet_nbt import ListTag

from .utils import get_pos, get_world, iterate_chunks


def print_entry(e, empty, only_loot):
    if "Pos" in e:
        location = "{:s} at ({:0.0f}, {:0.0f}, {:0.0f})".format(
            e["id"].py_str.replace("minecraft:", "").replace("_", " ").title(),
            *[v.py_float for v in e["Pos"].py_list]
        )
    else:
        location = "{:s} at ({x:0.0f}, {y:0.0f}, {z:0.0f})".format(
            e["id"].py_str.replace("minecraft:", "").replace("_", " ").title(), **e
        )
    if "Items" in e and not only_loot:
        content = Counter()
        for i in e["Items"]:
            content.update({i["id"]: i["Count"]})
        if content:
            print(location)
            for k, v in content.most_common():
                print("- {}: {:d}".format(k.replace("minecraft:", "").replace("_", " ").title(), v))
        elif empty:
            print(location)
            print(" Empty")
    elif "LootTable" in e:
        print(location)
        print(
            "- Loot from {} table".format(
                e["LootTable"]
                .py_str.split("/")[-1]
                .replace("minecraft:", "")
                .replace("_", " ")
                .title()
            )
        )


def main(save_folder, dimension, center, distance, empty, only_loot) -> int:
    world = get_world(save_folder, dimension)
    pos = get_pos(save_folder, dimension, center)
    print("\nEntities:")
    for _, chunk in iterate_chunks(world.entities, pos, distance):
        for e in (
            chunk.get("TileEntities", ListTag()).py_list + chunk.get("Entities", ListTag()).py_list
        ):
            if "Items" in e or "LootTable" in e:
                print_entry(e, empty, only_loot)
    return 0
