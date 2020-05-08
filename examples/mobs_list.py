"""
Prints all mobs in the Overworld (Entities with Brain)
"""
import sys

import minenbt


def main(world_folder) -> int:
    save_folder = minenbt.SaveFolder(world_folder)
    world = save_folder.overworld()
    print("Entities:\n")
    for _, _, region in world.regions():
        for _, _, chunk in region.chunks():
            for e in chunk["Level"].get("Entities"):
                # Filter mobs
                if "Brain" in e:
                    print(
                        "{:s} at ({:0.1f}, {:0.1f}, {:0.1f})".format(
                            e["id"].replace("minecraft:", "").replace("_", " ").title(), *e["Pos"]
                        )
                    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Please add save folder argument")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
