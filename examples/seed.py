#!/usr/bin/env python
"""
Prints the seed of a world.
"""

import sys

import minenbt


def main(world_folder) -> int:
    save_folder = minenbt.SaveFolder(world_folder)
    print("Seed: {:d}".format(save_folder.level_dat().root["Data"]["RandomSeed"]))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Please add save folder argument")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
