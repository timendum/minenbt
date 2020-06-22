"""
Add one item to the single player inventory.
"""

from pathlib import Path

import minenbt
import nbtlib

from .utils import get_player, backup_write

# From https://minecraft.gamepedia.com/File:Items_slot_number.png
_SLOTS = set(range(9, 36))


def main(save_folder: minenbt.SaveFolder, item: str, count=1, uuid=None) -> int:
    level_dat, playerdata = get_player(save_folder, uuid)
    if level_dat:
        inventory = level_dat.root["Data"]["Player"]["Inventory"]
    else:
        inventory = playerdata.root["Inventory"]
    occupied_slots = set([int(i["Slot"]) for i in inventory])
    free_slots = _SLOTS - occupied_slots
    if not free_slots:
        print("No slot available in inventory")
        return 21
    new_slot = nbtlib.Compound(
        {
            "Slot": nbtlib.Byte(min(free_slots)),
            "id": nbtlib.String(item),
            "Count": nbtlib.Byte(count),
        }
    )
    inventory.append(new_slot)
    if level_dat:
        new_file = backup_write(level_dat)
    else:
        new_file = backup_write(playerdata)
    print("Backup at {}".format(new_file))
    return 0
