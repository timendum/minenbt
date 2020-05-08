"""
Prints all containers (chest, barrel, minecart with chest) in the Overworld
"""
import sys
from collections import Counter

import minenbt


def print_entry(e):
    if "Pos" in e:
        print(
            "{:s} at ({:0.1f}, {:0.1f}, {:0.1f})".format(
                e["id"].replace("minecraft:", "").replace("_", " ").title(), *e["Pos"]
            )
        )
    else:
        print(
            "{:s} at ({x:0.1f}, {y:0.1f}, {z:0.1f})".format(
                e["id"].replace("minecraft:", "").replace("_", " ").title(), **e
            )
        )
    if "Items" in e:
        content = Counter()
        for i in e["Items"]:
            content.update({i["id"]: i["Count"]})
        if content:
            for k, v in content.most_common():
                print("- {}: {:d}".format(k.replace("minecraft:", "").replace("_", " ").title(), v))
        else:
            print(" Empty")
    elif "LootTable" in e:
        print(
            "- Loot from {} table".format(
                e["LootTable"].split("/")[-1].replace("minecraft:", "").replace("_", " ").title()
            )
        )


def main(world_folder) -> int:
    save_folder = minenbt.SaveFolder(world_folder)
    world = save_folder.overworld()
    print("Entities:\n")
    for _, _, region in world.regions():
        for _, _, chunk in region.chunks():
            for e in chunk["Level"].get("TileEntities") + chunk["Level"].get("Entities"):
                if "Items" in e or "LootTable" in e:
                    print_entry(e)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Please add save folder argument")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
