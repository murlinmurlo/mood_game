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
    movemonsters on|off
    quit

Server command:
    move <x> <y>                             (0 <= x < 10, 0 <= y < 10)
    addmon <name> <x> <y> <message> <hp>     (0 <= x < 10, 0 <= y < 10, 0 < hp)
    attack <name> <weapon>                   (weapon correct)
    sayall <message>
    movemonsters on|off
    quit
"""


import asyncio
from . import main


if __name__ == "__main__":
    asyncio.run(main())
