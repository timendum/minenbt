# minenbt

> A python library to read (and edit) Minecraft Java Edition files. Requires python 3.7.


## Features

- Parse `level.dat` ([player.dat format](https://minecraft.gamepedia.com/Player.dat_format)).
- Parse region file ([anvil format](https://minecraft.gamepedia.com/Anvil_file_format)) and chunks within the region.
- Parse `raids.dat` file ([raids format](https://minecraft.gamepedia.com/Raids.dat_format)).
- Parse poi file ([anvil format](https://minecraft.gamepedia.com/Anvil_file_format)).
- Includes examples to quickly perform analysis, listing, etc. (check `cli` folder).
- Based on [nbtlib](https://github.com/vberlier/nbtlib/) library.
- Inspired by [twoolie's NBT](https://github.com/twoolie/NBT).


## Basic usage

### List inventory for single-player saves.

```python
import minenbt

save_folder = minenbt.SaveFolder("SaveInstance")
dat = save_folder.level_dat()
inventory = dat.root["Data"]["Player"]["Inventory"]
```

## Command line utility

### How to install

1. Go to [latest release](https://github.com/timendum/minenbt/releases/latest)
1. Download "`win-amd64.zip`"
1. Extract the zip file anywhere
1. Run  `minenbt.exe <SAVE_PATH> <command>`, `SAVE_PATH` must be a Minecraft save folder (eg: `%appdata%\.minecraft\saves\<Name>`)

### Commands:

- `info`  
General information about the world.
- `biome`  
Count the number of biomes in a dimension.
- `add`  
Add one item to the single player inventory.
- `containers`  
Prints all containers
- `mobs`  
Prints all mobs in the Overworld
- `structures`  
Prints all structures
- `block`  
Find blocks by id
- `repair`  
Repair all items in the single player's inventory.

### Examples

`SPATH` is a Minecraft save folder (eg: `%appdata%\.minecraft\saves\<Name>`).

#### Print general info about the save and world:

    minenbt.exe SPATH info

#### Add a shield to a single player inventory

    minenbt.exe SPATH add minecraft:shield

#### Add a stack of sand to a single player inventory

    minenbt.exe SPATH add minecraft:sand -c 64

#### Repair every item in a single player inventory

This command will set an almost full durability bar for every item in a single player inventory.

    minenbt.exe SPATH repair

#### Find a near diamond ore

This command will print all diamond ore with a horizontal distance from the player lesser then 20 (circa).

    minenbt.exe SPATH block minecraft:diamond_ore -l 20