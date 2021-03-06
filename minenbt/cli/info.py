"""
Prints general information about the world.
"""

import minenbt

from .utils import dimension_player, pos_player


def main(save_folder: minenbt.SaveFolder) -> int:
    data = save_folder.level_dat().root["Data"]
    if "generatorName" in data:
        # Until MC 1.15.2
        print("World type: {}".format(data["generatorName"].replace("_", " ").title()))
    game_type = {0: "Survival", 1: "Creative", 2: "Adventure", 3: "Spectator"}[data["GameType"]]
    print("Game type: {}".format(game_type))
    difficulty = {0: "Peaceful", 1: "Easy", 2: "Normal", 3: "Hard"}[data["Difficulty"]]
    print("Difficulty: {}".format(difficulty))
    print("Cheat enabled: {}".format("Yes" if data["allowCommands"] else "No"))
    print("Hours played: {:,.1f}".format(data["Time"] / 20 / 60 / 60))
    if "RandomSeed" in data:
        # Until MC 1.15.2
        seed = data["RandomSeed"]
    else:
        # From 1.16
        seed = data["WorldGenSettings"]["seed"]
    print("Seed: {:d}".format(seed))
    print("DataVersion: {:d}".format(data["DataVersion"]))
    dimension = dimension_player(save_folder)
    if dimension:
        print("Player found in {}".format(dimension.title()))
    pos = pos_player(save_folder)
    if pos:
        print("Player at ({:0.0f}, {:0.0f}, {:0.0f})".format(*pos))
    print("Players UUIDs:")
    for p in save_folder.players():
        print("- {}".format(p))
    return 0
