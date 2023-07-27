"""
Repair all items in the single player's inventory.
"""

from typing import TYPE_CHECKING

from amulet_nbt import IntTag

if TYPE_CHECKING:
    import minenbt

from .utils import backup_save, find_player, get_player_file


def main(save_folder: "minenbt.SaveFolder", uuid) -> int:
    level_dat, playerdata = get_player_file(save_folder, uuid)
    inventory = find_player(level_dat, playerdata)["Inventory"]
    for item in inventory:
        if "tag" not in item:
            continue
        if "Damage" not in item["tag"]:
            continue
        item["tag"]["Damage"] = IntTag(min(item["tag"]["Damage"].py_int, 1))
    new_file = backup_save(level_dat, playerdata)
    print(f"Backup at {new_file}")
    return 0
