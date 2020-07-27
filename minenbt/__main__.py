import argparse

import minenbt.cli as cli
from minenbt import SaveFolder


def __add_dimension(parser):
    parser.add_argument("-d", "--dimension", choices=["overworld", "the_nether", "the_end"])


def __add_uuid(parser):
    parser.add_argument("-i", "--uuid", help="UUID of the player (default: Signle player)")


def __add_center(parser):
    parser.add_argument(
        "-c",
        "--center",
        type=cli.utils.Center,
        help="Print first results nearer from this position (Default=single player position)",
    )


def __add_center_distance(parser):
    __add_center(parser)
    parser.add_argument(
        "-l",
        "--distance",
        type=int,
        help="Only result within horizontal distance block from the center will be printed.",
    )


def main():
    parser = argparse.ArgumentParser("minenbt")
    parser.add_argument("save_folder", type=SaveFolder)
    subparsers = parser.add_subparsers(help="Modules:")
    # info
    info_parser = subparsers.add_parser("info", help=cli.info.__doc__.strip())
    info_parser.set_defaults(func=cli.info.main)
    # biome_analysis
    biome_parser = subparsers.add_parser("biome", help=cli.biome_analysis.__doc__.strip())
    biome_parser.set_defaults(func=cli.biome_analysis.main)
    __add_dimension(biome_parser)
    # add_to_inventory
    add_parser = subparsers.add_parser("add", help=cli.add_to_inventory.__doc__.strip())
    add_parser.set_defaults(func=cli.add_to_inventory.main)
    add_parser.add_argument("item", help="Item id (es: minecraft:arrow)")
    add_parser.add_argument("-c", "--count", help="How many items", default=1)
    __add_uuid(add_parser)
    # containers
    containers_parser = subparsers.add_parser(
        "containers", help=cli.containers_list.__doc__.strip()
    )
    containers_parser.set_defaults(func=cli.containers_list.main)
    __add_dimension(containers_parser)
    __add_center_distance(containers_parser)
    containers_group = containers_parser.add_mutually_exclusive_group()
    containers_group.add_argument(
        "-e", "--empty", action="store_true", help="Print also empty chests."
    )
    containers_group.add_argument(
        "-o", "--only_loot", action="store_true", help="Print only chests with loot."
    )
    # mobs
    mobs_parser = subparsers.add_parser("mobs", help=cli.mobs_list.__doc__.strip())
    mobs_parser.set_defaults(func=cli.mobs_list.main)
    __add_dimension(mobs_parser)
    __add_center_distance(mobs_parser)
    # structures
    structures_parser = subparsers.add_parser("structures", help=cli.structure_list.__doc__.strip())
    structures_parser.set_defaults(func=cli.structure_list.main)
    __add_dimension(structures_parser)
    __add_center_distance(structures_parser)
    # block
    block_parser = subparsers.add_parser("block", help=cli.find_block.__doc__.strip())
    block_parser.set_defaults(func=cli.find_block.main)
    __add_dimension(block_parser)
    __add_center_distance(block_parser)
    block_parser.add_argument("block_id", help="Block ID")
    # repair
    repair_parser = subparsers.add_parser("repair", help=cli.repair.__doc__.strip())
    __add_uuid(repair_parser)
    repair_parser.set_defaults(func=cli.repair.main)
    # dumpr
    dumpr_parser = subparsers.add_parser("dumpr", help=cli.dumpr.__doc__.strip())
    dumpr_parser.set_defaults(func=cli.dumpr.main)
    __add_dimension(dumpr_parser)
    __add_center(dumpr_parser)
    dumpr_parser.add_argument("ltype", help="Location type", choices=["chunk", "sector", "block"])
    dumpr_parser.add_argument(
        "-p", "--pretty-print", action="store_true", help="Pretty print output."
    )
    # dumpr
    dumpl_parser = subparsers.add_parser("dumpl", help=cli.dumpl.__doc__.strip())
    dumpl_parser.set_defaults(func=cli.dumpl.main)
    __add_uuid(dumpl_parser)
    dumpl_parser.add_argument("etype", help="Entity type", choices=["level", "player", "inventory"])
    dumpl_parser.add_argument(
        "-p", "--pretty-print", action="store_true", help="Pretty print output."
    )
    # parse
    args = parser.parse_args()
    if "func" in args:
        dargs = {**vars(args)}
        del dargs["func"]
        try:
            return args.func(**dargs)
        except FileNotFoundError:
            parser.exit(
                11, "Error: save_folder is not a valid save folder, it should contains level.dat"
            )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
