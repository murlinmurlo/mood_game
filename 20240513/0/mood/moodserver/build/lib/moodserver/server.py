#!/usr/bin/env python3

import cowsay as cs
import shlex
import asyncio
import threading
import locale
import gettext
import os
from collections import defaultdict
from typing import Optional, Tuple, TypeAlias
from time import sleep
from random import choice


# === States ===
State: TypeAlias = int

NEW_USER = 1


popath = os.path.join(os.path.dirname(__file__), "po")
ENG = gettext.translation("server", popath, languages=["en"], fallback=True)
RU = gettext.translation("server", popath, languages=["ru"], fallback=True)

list_cows = cs.list_cows() + ["jgsbat"]
WEAPONS = {
    "sword": 10,
    "spear": 15,
    "axe": 20,
}


class Client:

    """
    A client object, representing a player in a multiplayer game. Each client has a name, address, hero object, and writer
    object for sending messages to other clients.

    Attributes:
        client_list: (dict) A class-level dictionary mapping client names to client objects.
    """

    client_list = {}

    def __init__(self, name: str, addr: str) -> None:
        """
        Initializes a new client with the given name, address, and hero object. Adds the client to the client list.

            :param name: (str) The name of the client.
            :param addr: (str) The address of the client.
        """
        self.name = name
        self.addr = addr
        self.hero = None
        self.writer = None
        self.locale = ENG
        Client.client_list.update({name: self})

    @staticmethod
    def connect(name: str, addr: str) -> bool:
        """
        Static method that creates a new client and adds it to the client list with the given name and address.

            :param name: (str) The name of the client to be added.
            :param addr: (str) The address of the client to be added.
            :return: (bool) True if the client was successfully added to the client list, False otherwise.
        """

        if name in Client.client_list:
            return False

        Client(name, addr)
        return True

    @staticmethod
    def meta(name: str):
        """
        Static method that retrieves the client with the given name from the client list.

            :param name: (str) The name of the client to be retrieved.
            :return: (Client or None) The client object with the given name if it exists in the client list, or None otherwise.
        """

        if name in Client.client_list:
            return Client.client_list[name]

    @staticmethod
    def disconnect(name: str) -> None:
        """
        Static method that removes the client with the given name from the client list.

            :param name: (str) The name of the client to be removed.
            :return: None
        """

        if Client.meta(name):
            Client.client_list.pop(name)

    def __str__(self) -> str:
        """
        Returns a string representation of the client object.

            :return: (str) A string representation of the client object.
        """

        name = f"Name     : {self.name}"
        addr = f"Address  : {self.addr}"
        pos = f"Position : {self.hero.pos}"

        return "\n".join((name, addr, pos)) + "\n"

    def broadcast(self, msg: str, state: State = None) -> None:
        """
        Sends a message to all clients in the client list except for the calling client.

            :param self: (Client) The client sending the message.
            :param msg: (str) The message to be sent to other clients.
            :return: None
        """

        for _, obj in filter(lambda u: u[0] != self.name, Client.client_list.items()):
            obj.writer.write(msg.encode())


class Hero:
    """
    A hero object, representing the player's character in a multiplayer game.

    Attributes:
        WEAPONS: (dict) A class-level dictionary mapping weapon names to damage values.
    """

    WEAPONS = WEAPONS

    def __init__(self) -> None:
        """
        Initializes a new hero with the default position of [0, 0].
        """
        self.pos = [0, 0]


class Monster:
    """
    A monster object, representing an enemy character in a multiplayer game.

    Attributes:
        monsters: (list) - list of monsters.
    """

    monsters = []

    def __init__(
        self, name: str, hello_string: str, hp: int, coords: list[int]
    ) -> None:
        """
        Initializes a new monster with the given name, greeting message, hitpoints, and coordinates.

        :param name: (str) The name of the monster.
        :param hello_string: (str) The greeting string that the monster outputs.
        :param hp: (int) The hitpoints of the monster.
        :param coords: (tuple) The coordinates of the monster on the field in the format (x, y).
        """

        self.name = name
        self.msg = hello_string
        self.hp = hp
        self.coords = coords
        Monster.monsters.append(self)


class Game:
    """
    Game class for MOOD.

    Attributes:
        ways (dict): dictionary of possible directions
        field (list): game field

    """

    ways = {
        "up": (0, 1),
        "down": (0, -1),
        "right": (1, 0),
        "left": (-1, 0),
    }

    field = [[None] * 10 for _ in range(10)]

    def __init__(self, player: Optional[Client]) -> None:
        """
        Initializes player for the game

        :param player: (Client) client instance for player
        """
        self.player = player

    def add_monster(self, monster: Optional[Monster]) -> str:
        """
        Adds monster to the game field

        :param monster: (Monster) monster instance
        :return: (str) message regarding monster addition
        """

        i, j = monster.coords
        new = False
        if self.field[i][j]:
            new = True

        self.field[i][j] = monster

        return monster.name, monster.coords, monster.msg, new

    def encounter(self, x: int, y: int) -> tuple[str]:
        """
        Checks if there is a monster at a specific location and returns monster message and name


        :param x: (int) x-coordinate
        :param y: (int) y-coordinate
        :return: (str, str) monster message and name
        """

        return self.field[x][y].msg, self.field[x][y].name

    def change_hero_pos(self, way: str) -> str:
        """
        Changes hero's position on the field

        :param way: (str) direction of movement
        :return: (str) message regarding hero's movement and possible encounter with monster
        """

        x, y = Game.ways[way]

        i = self.player.hero.pos[0] = (x + self.player.hero.pos[0]) % 10
        j = self.player.hero.pos[1] = (y + self.player.hero.pos[1]) % 10

        msg = ""
        if self.field[i][j]:
            text, name = self.encounter(i, j)
            msg += cs.cowsay(message=text, cow=name)

        return i, j, msg

    def attack(self, pos: tuple[int], name: str, dmg: int) -> tuple[str]:
        """
        Carries out an attack on a monster at a specific location

        :param pos: (int, int) monster coordinates in the field
        :param name: (str) monster name
        :param dmg: (int) damage to be inflicted
        :return: (str, bool) message regarding the attack and boolean flag indicating whether the attack was carried out or not
        """

        data = {}
        data["died"] = False

        data["here"] = data["here_name"] = False
        i, j = pos
        flag = False
        if monster := self.field[i][j]:
            data["here"] = True
            if monster.name == name:
                data["here_name"] = True
                dmg = dmg if monster.hp > dmg else monster.hp
                monster.hp -= dmg
                data["name"] = monster.name
                data["dmg"] = dmg

                if monster.hp == 0:
                    data["died"] = True
                    self.field[i][j] = None
                else:
                    data["hp"] = monster.hp
                flag = True
            else:
                data["name"] = name

        return data, flag


def monster_moving(delay=30):
    dangeon = Game(None)
    monsters = Monster.monsters
    while True:
        if monsters:
            monster = choice(monsters)
            x, y = monster.coords
            move = choice(list(Game.ways.items()))
            _x, _y = move[1][0], move[1][1]
            new_x, new_y = (x + _x) % 10, (y + _y) % 10

            if not Game.field[new_x][new_y]:
                msg = f"{monster.name} moved one cell {move[0]}"
                monster.coords = (new_x, new_y)
                Game.field[new_x][new_y] = monster
                Game.field[x][y] = None

                for _, obj in Client.client_list.items():
                    obj.writer.write(msg.encode())

                text, name = dangeon.encounter(*monster.coords)
                msg = cs.cowsay(message=text, cow=name)
                for _, obj in filter(
                    lambda u: tuple(u[1].hero.pos) == monster.coords,
                    Client.client_list.items(),
                ):
                    obj.writer.write(msg.encode())

            else:
                continue

        sleep(delay)


async def echo(reader, writer):
    host, port = writer.get_extra_info("peername")
    print(f"New connection from {host}:{port}")
    usr = await reader.readline()
    usr = usr.decode().strip()

    if not Client.connect(usr, f"{host}:{port}"):
        writer.write(f"User with login {usr} already exists.\n".encode())
        print(f"Disconnect {host}:{port}")
        writer.close()
        await writer.wait_closed()

    else:
        clt = Client.meta(usr)
        clt.hero = Hero()
        clt.writer = writer

        clt.locale.install()
        meta = str(Client.meta(usr)) + "\n"
        writer.write(meta.encode())
        clt.broadcast(meta, NEW_USER)

        dungeon = Game(clt)
        while not reader.at_eof():
            data = await reader.readline()
            msg = shlex.split(data.decode().strip())
            ans = ""
            match msg:
                case way if len(way) == 1 and way[0] in Game.ways:
                    i, j, msg = dungeon.change_hero_pos(way[0])
                    clt.locale.install()
                    ans = _("Moved to ({}, {})").format(i, j)
                    writer.write((ans + msg).encode())
                    await writer.drain()

                case ["addmon", *args]:
                    if len(args) == 8:
                        if args[0] in list_cows:
                            name, coords, msg, new = dungeon.add_monster(
                                Monster(
                                    args[0],
                                    args[args.index("hello") + 1],
                                    int(args[args.index("hp") + 1]),
                                    (
                                        int(args[args.index("coords") + 1]),
                                        int(args[args.index("coords") + 2]),
                                    ),
                                )
                            )

                            clt.locale.install()
                            ans = _("Added monster {} to {} saying {}.").format(
                                name, coords, msg
                            )
                            if new:
                                ans += _("\nReplaced the old monster")

                            writer.write(ans.encode())
                            clt.broadcast((clt.name + ": " + ans).encode())

                case ["attack", *args]:
                    data, flag = dungeon.attack(clt.hero.pos, args[0], int(args[1]))

                    if not data["here"]:
                        ans = _("No monster here")
                    elif not data["here_name"]:
                        ans = _("No {} here").format(data["name"])
                    else:
                        ans = _("Attacked {}, damage {} hp").format(
                            data["name"], data["dmg"]
                        )
                        if data["died"]:
                            ans += "\n" + _("{} died.").format(data["name"])
                        else:
                            ans += "\n" + _("{} now has {} hp").format(
                                data["name"], data["hp"]
                            )

                    if flag:
                        clt.broadcast((clt.name + ": " + ans).encode())

                    writer.write(ans.encode())
                    await writer.drain()

                case ["sayall", *text]:
                    clt.broadcast((clt.name + ": " + " ".join(text).strip()).encode())

                case ["locale", locale]:
                    if locale == "ru_RU.UTF8":
                        clt.locale = RU
                    else:
                        clt.locale = ENG

                    clt.locale.install()
                    writer.write(_("Set up locale: {}").format(locale).encode())
                    await writer.drain()

                case ["quit"]:
                    break

                case _:
                    ans = "Error"

        clt.broadcast(("Dissconnect:\n" + str(clt)).encode())
        writer.write("Goodbye".encode())
        Client.disconnect(usr)
        writer.close()
        await writer.wait_closed()


async def main():
    thr = threading.Thread(target=monster_moving, args=(30,))
    thr.start()
    server = await asyncio.start_server(echo, "0.0.0.0", 1337)
    async with server:
        await server.serve_forever()


def run():
    asyncio.run(main())

    
if __name__ == "__main__":
    asyncio.run(main())
