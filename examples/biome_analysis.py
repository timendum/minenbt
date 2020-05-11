"""
Counter the number of biomes in the (generated) world.
"""
import sys
import typing
from collections import Counter

import minenbt


# https://minecraft.gamepedia.com/Java_Edition_data_values#Biomes
BIOMES = {
    0: "Ocean",
    1: "Plains",
    2: "Desert",
    3: "Mountains",
    4: "Forest",
    5: "Taiga",
    6: "Swamp",
    7: "River",
    8: "Nether",
    9: "The End",
    10: "Frozen Ocean",
    11: "Frozen River",
    12: "Snowy Tundra",
    13: "Snowy Mountains",
    14: "Mushroom Fields",
    15: "Mushroom Field Shore",
    16: "Beach",
    17: "Desert Hills",
    18: "Wooded Hills",
    19: "Taiga Hills",
    20: "Mountain Edge",
    21: "Jungle",
    22: "Jungle Hills",
    23: "Jungle Edge",
    24: "Deep Ocean",
    25: "Stone Shore",
    26: "Snowy Beach",
    27: "Birch Forest",
    28: "Birch Forest Hills",
    29: "Dark Forest",
    30: "Snowy Taiga",
    31: "Snowy Taiga Hills",
    32: "Giant Tree Taiga",
    33: "Giant Tree Taiga Hills",
    34: "Wooded Mountains",
    35: "Savanna",
    36: "Savanna Plateau",
    37: "Badlands",
    38: "Wooded Badlands Plateau",
    39: "Badlands Plateau",
    40: "Small End Islands",
    41: "End Midlands",
    42: "End Highlands",
    43: "End Barrens",
    44: "Warm Ocean",
    45: "Lukewarm Ocean",
    46: "Cold Ocean",
    47: "Deep Warm Ocean",
    48: "Deep Lukewarm Ocean",
    49: "Deep Cold Ocean",
    50: "Deep Frozen Ocean",
    127: "The Void",
    129: "Sunflower Plains",
    130: "Desert Lakes",
    131: "Gravelly Mountains",
    132: "Flower Forest",
    133: "Taiga Mountains",
    134: "Swamp Hills",
    140: "Ice Spikes",
    149: "Modified Jungle",
    151: "Modified Jungle Edge",
    155: "Tall Birch Forest",
    156: "Tall Birch Hills",
    157: "Dark Forest Hills",
    158: "Snowy Taiga Mountains",
    160: "Giant Spruce Taiga",
    161: "Giant Spruce Taiga Hills",
    162: "Gravelly Mountains+",
    163: "Shattered Savanna",
    164: "Shattered Savanna Plateau",
    165: "Eroded Badlands",
    166: "Modified Wooded Badlands Plateau",
    167: "Modified Badlands Plateau",
    168: "Bamboo Jungle",
    169: "Bamboo Jungle Hills",
}


def main(world_folder) -> int:
    save_folder = minenbt.SaveFolder(world_folder)
    world = save_folder.overworld()
    biomes: typing.Counter[int] = Counter()
    print("Reading Overworld...", end="\r")
    lregions = len(list(world.regions()))
    i = 0
    for rx, ry, region in world.regions():
        i += 1
        print("Reading Overworld... {:0>3}/{}".format(i, lregions), end="\r")
        for _, _, chunk in region.chunks():
            if chunk:
                biomes.update(chunk["Level"].get("Biomes"))

    print("Biomes:                         \n")
    # must be long enought to overwrite last line
    swidth = max(len(s) for s in BIOMES.values())
    for biome, value in biomes.most_common():
        print("{0:<{swidth}}: {1:>10,d}".format(BIOMES[biome], value, swidth=swidth))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Please add save folder argument")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))