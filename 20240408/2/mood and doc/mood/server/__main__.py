"""
Client for MUD (multi user dungeon).

Client commands:
help - shows the help
left, right, down, up - movement
addmon - add a monster
<name> - monster name
coords <x> <y> - monster coordinates
hello <message> - monster greeting message
hp <hp> - monster health points
attack <name> [with weapon] - attack a monster
sayall <message> - message to all players
quit - exit the game

For more information, use the "help" command.
"""

import argparse
import asyncio
from . import main, run_server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='MOOD',
                                     description='Server for MOOD (multi user dangeon)')
    parser.add_argument('--disable_wandering_monster', action='store_true')
    args = parser.parse_args()
    if args.disable_wandering_monster:
        asyncio.run(run_server())
    else:
        asyncio.run(main())
