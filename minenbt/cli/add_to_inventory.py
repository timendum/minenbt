"""
Add one item to the single player inventory.
"""

from pathlib import Path

import minenbt
import nbtlib

# From https://minecraft.gamepedia.com/File:Items_slot_number.png
_SLOTS = set(range(9, 36))


def main(save_folder: minenbt.SaveFolder, item: str, count=1) -> int:
    dat = save_folder.level_dat()
    if "Player" not in dat.root["Data"]:
        print("The Save is not for single player.")
        return 20
    inventory = dat.root["Data"]["Player"]["Inventory"]
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
    new_file = Path("level.dat_new")
    dat.save(new_file)
    print("Saved as {}".format(new_file.absolute()))
    return 0
