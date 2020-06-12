"""
Repair all items in the single player's inventory.
"""

from pathlib import Path

import minenbt
import nbtlib


def main(save_folder: minenbt.SaveFolder) -> int:
    dat = save_folder.level_dat()
    if "Player" not in dat.root["Data"]:
        print("The Save is not for single player.")
        return 20
    inventory = dat.root["Data"]["Player"]["Inventory"]
    for item in inventory:
        if "tag" not in item:
            continue
        if "Damage" not in item["tag"]:
            continue
        item["tag"]["Damage"] = min(item["tag"]["Damage"], nbtlib.Int(1))
    new_file = Path("level.dat_new")
    dat.save(new_file)
    print("Saved as {}".format(new_file.absolute()))
    return 0
