"""
Prints general information about the world.
"""

import minenbt

from .utils import dimension_player, pos_player


def main(save_folder: minenbt.SaveFolder) -> int:
    data = save_folder.level_dat().tag.compound["Data"]
    if "generatorName" in data:
        # Until MC 1.15.2
        print("World type: {}".format(data["generatorName"].replace("_", " ").title()))
    game_type = {0: "Survival", 1: "Creative", 2: "Adventure", 3: "Spectator"}[data["GameType"].py_int]
    print(f"Game type: {game_type}")
    difficulty = {0: "Peaceful", 1: "Easy", 2: "Normal", 3: "Hard"}[data["Difficulty"].py_int]
    print(f"Difficulty: {difficulty}")
    print("Cheat enabled: {}".format("Yes" if data["allowCommands"] else "No"))
    print("Hours played: {:,.1f}".format(data["Time"] / 20 / 60 / 60))
    if "RandomSeed" in data:
        # Until MC 1.15.2
        seed = data["RandomSeed"].py_int
    else:
        # From 1.16
        seed = data["WorldGenSettings"]["seed"].py_int
    print(f"Seed: {seed:d}")
    print("DataVersion: {:d}".format(data["DataVersion"].py_int))
    dimension = dimension_player(save_folder)
    if dimension:
        print(f"Player found in {dimension.title()}")
    pos = pos_player(save_folder)
    if pos:
        print("Player at ({:0.0f}, {:0.0f}, {:0.0f})".format(*pos))
    print("Players UUIDs:")
    for p in save_folder.players():
        print(f"- {p}")
    return 0
