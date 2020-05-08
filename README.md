# minenbt

> A python library to read (and edit) Minecraft Java Edition files. Requires python 3.7.


## Features

- Parse `level.dat` ([player.dat format](https://minecraft.gamepedia.com/Player.dat_format)).
- Parse region file ([anvil format](https://minecraft.gamepedia.com/Anvil_file_format)) and chunks within the region.
- Parse `raids.dat` file ([raids format](https://minecraft.gamepedia.com/Raids.dat_format)).
- Parse poi file ([anvil format](https://minecraft.gamepedia.com/Anvil_file_format)).
- Includes exemplase to quickly perform analysis, listing, etc (check `examples` folder).
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
