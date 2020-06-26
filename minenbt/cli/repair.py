"""
Repair all items in the single player's inventory.
"""

import nbtlib

import minenbt

from .utils import backup_write, get_player


def main(save_folder: minenbt.SaveFolder, uuid) -> int:
    level_dat, playerdata = get_player(save_folder, uuid)
    if level_dat:
        inventory = level_dat.root["Data"]["Player"]["Inventory"]
    else:
        inventory = playerdata.root["Inventory"]
    for item in inventory:
        if "tag" not in item:
            continue
        if "Damage" not in item["tag"]:
            continue
        item["tag"]["Damage"] = min(item["tag"]["Damage"], nbtlib.Int(1))
    if level_dat:
        new_file = backup_write(level_dat)
    else:
        new_file = backup_write(playerdata)
    print("Backup at {}".format(new_file))
    return 0
