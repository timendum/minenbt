"""
Dump a Minecraft level.dat data.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from minenbt import SaveFolder

from .utils import get_player_file, json_pprint, json_print


def main(save_folder: "SaveFolder", etype, uuid, pretty_print) -> int:
    pprint = json_print
    if pretty_print:
        pprint = json_pprint

    level_dat = save_folder.level_dat().tag
    if etype == "level":
        pprint(level_dat)
        return 0
    if etype == "player":
        level_dat, playerdata = get_player_file(save_folder, uuid)
        if level_dat:
            player = level_dat.compound["Data"]["Player"]
        else:
            player = playerdata.tag
        pprint(player)
        return 0
    if etype == "inventory":
        level_dat, playerdata = get_player_file(save_folder, uuid)
        if level_dat:
            inventory = level_dat.compound["Data"]["Player"]["Inventory"]
        else:
            inventory = playerdata.tag["Inventory"]
        pprint(inventory)
    return -1
