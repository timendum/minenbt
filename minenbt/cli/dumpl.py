"""
Dump a Minecraft level.dat data.
"""

import minenbt

from .utils import get_player
from .dumpr import CustomJSONEncoder


def main(save_folder: minenbt.SaveFolder, etype, uuid, pretty_print) -> int:
    encoder = CustomJSONEncoder()

    def pprint(o):
        print(encoder.encode(o))

    if pretty_print:
        encoder.indent = 4

    level_dat = save_folder.level_dat().root
    if etype == "level":
        pprint(level_dat)
        return 0
    if etype == "player":
        level_dat, playerdata = get_player(save_folder, uuid)
        if level_dat:
            player = level_dat.root["Data"]["Player"]
        else:
            player = playerdata.root
        pprint(player)
        return 0
    if etype == "inventory":
        level_dat, playerdata = get_player(save_folder, uuid)
        if level_dat:
            inventory = level_dat.root["Data"]["Player"]["Inventory"]
        else:
            inventory = playerdata.root["Inventory"]
        pprint(inventory)
    return -1
