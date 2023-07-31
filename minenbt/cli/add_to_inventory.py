"""
Add one item to the single player inventory.
"""

from typing import TYPE_CHECKING

import amulet_nbt

if TYPE_CHECKING:
    import minenbt

from .utils import backup_save, find_player, get_player_file

# From https://minecraft.fandom.com/File:Items_slot_number.png
_SLOTS = set(range(9, 36))


def main(save_folder: "minenbt.SaveFolder", item: str, count=1, uuid=None) -> int:
    level_dat, playerdata = get_player_file(save_folder, uuid)
    inventory = find_player(level_dat, playerdata)["Inventory"]
    occupied_slots = set([i["Slot"].py_int for i in inventory])
    free_slots = _SLOTS - occupied_slots
    if not free_slots:
        print("No slot available in inventory")
        return 21
    new_slot = amulet_nbt.CompoundTag(
        {
            "Slot": amulet_nbt.ByteTag(min(free_slots)),
            "id": amulet_nbt.StringTag(item),
            "Count": amulet_nbt.ByteTag(count),
        }
    )
    inventory.append(new_slot)
    new_file = backup_save(level_dat, playerdata)
    print(f"Backup at {new_file}")
    return 0
