"""
Server for MUD (multi user dangeon).

Client command:
    help
    left
    right
    down
    up
    addmon <name>
        coords <x> <y>              (non-positional)
        hello <message>             (non-positional)
        hp <hp>                     (non-positional)
    attack <name> [with weapon]     (default weapon - sword)
    sayall <message>
    quit

Server command:
    move <x> <y>                             (0 <= x < 10, 0 <= y < 10)
    addmon <name> <x> <y> <message> <hp>     (0 <= x < 10, 0 <= y < 10, 0 < hp)
    attack <name> <weapon>                   (weapon correct)
    sayall <message>
    quit
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
