"""MOOD server"""
import shlex
import asyncio
import random
import gettext
from pathlib import Path
from ..common import (get_all_monster_names,
                      get_cowsay_msg,
                      TIME_INTERVAL_FOR_MOVING_MONSTER,
                      FIELD_SIZE)

_podir = str(Path(__file__).parents[1])
LOCALE = {
        "ru_RU.UTF-8": gettext.translation("mood", _podir, ["ru"], fallback=True),
        "default": gettext.NullTranslations()
}


def _(locale, text):
    """
    Translate the given text to the specified locale.

    :param locale: The locale to translate the text to.
    :param text: The text to be translated.
    :return: The translated text.
    """
    return LOCALE.get(locale, LOCALE["default"]).gettext(text)


def ngettext(locale, *args):
    """
    Translate plural forms with the specified locale.

    :param locale: The name of the locale or 'default'.
    :return: The translated plural form.
    """
    return LOCALE.get(locale, LOCALE["default"]).ngettext(*args)


async def put_broadcast(msg):
    """
    Send a message to all clients.

    :param msg: The message to be sent.
    """
    for client_id in clients:
        await clients_queue[client_id].put(msg)


class Field:
    """
    A main class that implements the game logic.

    It represents the dungeon field with players and monsters.
    It stores the positions of monsters, and provides methods to add, delete, and retrieve monsters from the field.
    """

    size: int = FIELD_SIZE
    """The width of the field."""

    def __init__(self):
        """Initialize the Field object."""
        self.field = [[0 for i in range(self.size)] for j in range(self.size)]
        self.monsters_pos = {}

    async def add_monster(self, x, y, monster, id):
        """
        Add a monster to the field.

        :param x: The x-coordinate of the cell where the monster should be added.
        :param y: The y-coordinate of the cell where the monster should be added.
        :param monster: The Monster object representing the monster to be added.
        :param id: The identifier of the client who is adding the monster.
        """
        if monster.get_name() in get_all_monster_names():
            subst = False
            if (x, y) in self.monsters_pos:
                subst = True
            self.monsters_pos[(x, y)] = monster
            for client_id in clients:
                locale = clients[client_id].get_locale()
                await clients_queue[client_id].put(ngettext(
                    locale,
                    "{} added monster {} to ({}, {}) saying {} with {} hp",
                    "{} added monster {} to ({}, {}) saying {} with {} hps", monster.get_hp()).format(
                 clients[id].get_name(),
                 monster.get_name(),
                 x, y,
                 monster.get_phrase(),
                 monster.get_hp()))
                if subst:
                    await clients_queue[client_id].put(_(locale, "Replaced the old monster"))
        else:
            await clients_queue[id].put(_(clients[id].get_locale(), "Cannot add unknown monster"))

    def delete_mon(self, coords):
        """
        Delete a monster from the field.

        :param coords: The coordinates of the monster to be deleted.
        """
        self.monsters_pos.pop(coords)

    def get_monster(self, pos):
        """
        Get the monster from a specific cell on the field.

        :param pos: The coordinates of the cell where the monster is located.
        :return: The instance of the Monster class representing the monster in the cell.
        """
        return self.monsters_pos[pos]

    def get_monsters_pos(self):
        """
        Get the positions of all the monsters on the field.

        :return: A dictionary-like object (key_dict) containing the positions of all the monsters.
        """
        return self.monsters_pos.keys()

    async def encounter(self, x, y, id):
        """
        If a player moves to a cell with a monster, send the player a notification.

        :param x: The x-coordinate of the player's position.
        :param y: The y-coordinate of the player's position.
        :param id: The identifier of the client who has encountered the monster.
        """
        pos = (x, y)
        if pos in self.get_monsters_pos():
            monster = self.get_monster(pos)
            msg = get_cowsay_msg(monster.get_name(), monster.get_phrase())
            await clients_queue[id].put(msg)

    async def wandering_monster(self):
        """
        Move a random monster every TIME_INTERVAL_FOR_MOVING_MONSTER seconds.

        If the monster ends up in a cell with a client, send them a notification.
        """
        monsters_pos = list(self.get_monsters_pos())
        if monsters_pos:
            chosed_monster_coords = random.choice(monsters_pos)
            chosed_monster_x, chosed_monster_y = chosed_monster_coords
            side, chosed_dir = random.choice(list(Player._dir_dict.items()))
            chosed_dir_x, chosed_dir_y = chosed_dir
            new_mon_coords = ((chosed_monster_x+chosed_dir_x) % self.size,
                              (chosed_monster_y+chosed_dir_y) % self.size)
            while new_mon_coords in monsters_pos:
                chosed_monster_coords = random.choice(monsters_pos)
                chosed_monster_x, chosed_monster_y = chosed_monster_coords
                side, chosed_dir = random.choice(list(Player._dir_dict.items()))
                chosed_dir_x, chosed_dir_y = chosed_dir
                new_mon_coords = ((chosed_monster_x+chosed_dir_x) % self.size,
                                  (chosed_monster_y+chosed_dir_y) % self.size)
            monster = self.get_monster(chosed_monster_coords)
            self.delete_mon(chosed_monster_coords)
            self.monsters_pos[new_mon_coords] = monster
            for client_id in clients:
                locale = clients[client_id].get_locale()
                await clients_queue[client_id].put(_(locale, "The monster {} has moved to the position {}").format(
                    monster.get_name(),
                    new_mon_coords))
                await self.encounter(*clients[client_id].get_coords(), client_id)


class Player:
    """
    A class that represents a player who can interact with the game field, monsters, and other players.

    :param field: A :class:`Field` object that represents the game field where the player is placed.
    :type field: :class:`Field`
    :param id: The unique identifier of the client associated with this player.
    :type id: str
    :param name: The login name of the client associated with this player.
    :type name: str
    """

    _dir_dict = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
    """
    A dictionary that maps direction names to the corresponding changes in x and y coordinates.
    """

    weapons = {"sword": 10, "spear": 15, "axe": 20}
    """
    A dictionary that maps weapon names to their corresponding damage values.
    """

    def __init__(self, field, id, name):
        """
        Initialize a new Player object.

        :param field: The game field where the player is placed.
        :type field: :class:`Field`
        :param id: The unique identifier of the client associated with this player.
        :type id: str
        :param name: The login name of the client associated with this player.
        :type name: str
        """
        self.x = 0
        self.y = 0
        self.field = field
        self.id = id
        self.name = name
        self.locale = 'default'

    def get_weapons(self):
        """
        Get the available weapons for the player to use in attacks.

        :return: A dictionary of available weapons and their corresponding damage values.
        """
        return self.weapons

    def get_name(self):
        """
        Get the login name of the client associated with this player.

        :return: The login name of the client.
        """
        return self.name

    def get_id(self):
        """
        Get the unique identifier of the client associated with this player.

        :return: The unique identifier of the client.
        """
        return self.id

    def get_coords(self):
        """
        Get the current coordinates of the player on the game field.

        :return: A tuple containing the player's current x and y coordinates.
        """
        return (self.x, self.y)

    def set_locale(self, locale):
        """
        Set the locale for the client associated with this player.

        :param locale: The new locale for the client.
        """
        self.locale = locale

    def get_locale(self):
        """
        Get the current locale for the client associated with this player.

        :return: The current locale for the client.
        """
        return self.locale

    async def make_move(self, x, y):
        """
        Move the player on the game field in the specified direction.

        :param x: The change in the x-coordinate for the move.
        :param y: The change in the y-coordinate for the move.
        """
        self.x += x
        self.y += y
        self.x %= Field.size
        self.y %= Field.size
        await clients_queue[self.id].put(_(self.get_locale(), "Moved to ({}, {})").format(
            self.x, self.y))
        await self.field.encounter(self.x, self.y, self.id)

    async def attack(self, name, weapon):
        """
        Perform an attack on a monster using the specified weapon.

        If there is no monster in the cell where the player is located, send a notification.

        :param name: The name of the monster to be attacked.
        :param weapon: The name of the weapon to be used in the attack.
        """
        damage = self.weapons[weapon]
        pos = (self.x, self.y)
        if (pos in self.field.get_monsters_pos() and
                self.field.get_monster(pos).get_name() == name):
            monster = self.field.get_monster(pos)
            damage = damage if monster.get_hp() > damage else monster.get_hp()
            for client_id in clients:
                locale = clients[client_id].get_locale()
                await clients_queue[client_id].put(ngettext(
                    locale,
                    "{} attacked {} with {}\ncausing {} hp damage",
                    "{} attacked {} with {}\ncausing {} hps damage", damage).format(
                 self.get_name(),
                 monster.get_name(),
                 weapon,
                 damage))
            await monster.get_damage(damage, self.id)
        else:
            locale = self.get_locale()
            await clients_queue[self.id].put(_(locale, "No {} here").format(name))

    async def sayall(self, msg):
        """
        Send a message to all users on the game field.

        :param msg: The message to be sent.
        """
        msg = f"{self.name}: {msg}"
        await put_broadcast(msg)


class Monster:
    """
    Class representing monster on the field.

    :param custom: specify if monster is custom, that is defined in other place
    :type custom: boolean
    :param kwargs: dict with info about monster

                'name' : monster name, must be correct name of default monsters or name of custom defined monster

                'pharse' : message which is being send to client while he meets monster in the field

                'coords' : coordinates where the monster should be placed

                'hp' : health points of the monster
    """

    def __init__(self,  **kwargs):
        """
        Initialize empty Monster object.

        Parameters:
            kwargs : dict with info about monster
                'name' : monster name, must be correct name of default monsters
                    or name of custom defined monster
                'pharse' : message which is being send to client while he
                    meets monster in the field
                'coords' : coordinates where the monster should be placed
                'hp' : health points of the monster
        """
        self.name = kwargs['name']
        self.phrase = kwargs['phrase']
        self.hp = kwargs['hp']
        self.coords = kwargs['coords']

    def get_phrase(self):
        """:return: monster's phrase."""
        return self.phrase

    def get_name(self):
        """:return: monster's name."""
        return self.name

    def get_hp(self):
        """:return: monster's hp."""
        return self.hp

    async def get_damage(self, damage, id):
        """
        Make monster get damage from the player.

        If after attack monster has 0 hp, deletes monster from the field
        """
        if damage < self.hp:
            self.hp -= damage
            for client_id in clients:
                locale = clients[client_id].get_locale()
                await clients_queue[client_id].put(
                        _(locale, "{} now has {}").format(self.get_name(), self.get_hp()))
        else:
            for client_id in clients:
                locale = clients[client_id].get_locale()
                await clients_queue[client_id].put(
                        _(locale, "{} died").format(self.get_name()))
            field.delete_mon(self.coords)


field = Field()

clients = {}          
clients_names = set()
clients_queue = {}              


async def play(reader, writer):
    """
    Handle the connection of a new player.

    This function is called when a new player connects to the server. It registers the client, checks if the
    given login is unique, creates asyncio tasks for sending, receiving, and broadcasting data. When the
    connection is lost, it deletes all data associated with the left client.

    :param reader: The reader object used to receive data from the client.
    :param writer: The writer object used to send data to the client.
    """
    client_id = "{}:{}".format(*writer.get_extra_info('peername'))
    print("Connection from: ", client_id)
    clients_queue[client_id] = asyncio.Queue()

    receive_data_from_client = asyncio.create_task(reader.readline())
    write_data_to_client = asyncio.create_task(clients_queue[client_id].get())
    await writer.drain()

    login_name, pending = await asyncio.wait([receive_data_from_client], return_when=asyncio.FIRST_COMPLETED)
    name = login_name.pop().result().decode().strip()
    if name not in clients_names:
        clients[client_id] = Player(field, client_id, name)
        clients_names.add(name)
        for id in clients:
            locale = clients[id].get_locale()
            await clients_queue[id].put(_(locale, "{} has joined the field").format(name))
    else:
        msg = "There are already user with this name in the game!"
        writer.write(msg.encode())
        receive_data_from_client.cancel()
        write_data_to_client.cancel()
        clients_names.remove(name)
        del clients_queue[client_id]
        del clients[client_id]
        writer.close()
        await writer.wait_closed()
        return

    async def execute_command(cmd):
        global daemon
        cmd = shlex.split(cmd)
        match cmd:
            case ['move', x, y]:
                x, y = int(x), int(y)
                await clients[client_id].make_move(int(x), int(y))
            case ['addmon', name, x, y, message, hp]:
                x, y, hp = int(x), int(y), int(hp)
                param_dict = {'coords': (x, y), 'hp': hp, 'phrase': message, 'name': name}
                await field.add_monster(x, y, Monster(**param_dict), client_id)
            case ['attack', name, weapon]:
                await clients[client_id].attack(name, weapon)
            case ['sayall', msg]:
                await clients[client_id].sayall(msg)
            case ['movemonsters', state]:
                if state == 'off':
                    daemon.cancel()
                    for id in clients:
                        locale = clients[id].get_locale()
                        await clients_queue[id].put(_(locale, "Moving monsters: off"))
                else:
                    if daemon.cancelled():
                        daemon = asyncio.create_task(moving_monster_daemon())
                        await asyncio.sleep(0)
                    for id in clients:
                        locale = clients[id].get_locale()
                        await clients_queue[id].put(_(locale, "Moving monsters: on"))
            case ['locale', loc]:
                clients[client_id].set_locale(loc)
                await clients_queue[client_id].put(_(loc, "Set up locale: {}").format(loc))
            case _:
                raise Exception

    receive_data_from_client = asyncio.create_task(reader.readline())
    while not reader.at_eof():
        done, pending = await asyncio.wait([receive_data_from_client, write_data_to_client], return_when=asyncio.FIRST_COMPLETED)
        for q in done:
            if q is receive_data_from_client:
                receive_data_from_client = asyncio.create_task(reader.readline())
                data = q.result().decode().strip()
                try:
                    await execute_command(data)
                except Exception as e:
                    print("Error occured\n", e)
                    await clients_queue[client_id].put(_(clients[client_id].get_locale(), "Something wrong with command"))
            else:
                data = q.result()
                while not clients_queue[client_id].empty():
                    data += '\n' + await clients_queue[client_id].get()
                write_data_to_client = asyncio.create_task(clients_queue[client_id].get())
                writer.write((data).encode())
            await writer.drain()

    print(f"disconnection: {name} ")
    for id in clients:
        locale = clients[id].get_locale()
        await clients_queue[id].put(_(locale, "{} disconnected").format(name))
    receive_data_from_client.cancel()
    write_data_to_client.cancel()
    clients_names.remove(name)
    del clients_queue[client_id]
    del clients[client_id]
    writer.close()
    await writer.wait_closed()


async def moving_monster_daemon():
    """
    A daemon that moves one random monster on the field.

    This daemon is responsible for invoking the `wandering_monster` method of the `Field` class, which moves one
    random monster on the game field. The daemon runs continuously, with a configurable time interval between
    each movement.
    """
    while True:
        print("Moving monsters")
        await field.wandering_monster()
        await asyncio.sleep(TIME_INTERVAL_FOR_MOVING_MONSTER)


async def main():
    """
    The main entry point of the server.

    This function creates the server, starts the moving monster daemon, and runs the server forever.
    """
    print("Start server")
    server = await asyncio.start_server(play, '0.0.0.0', 1337)
    global daemon
    daemon = asyncio.create_task(moving_monster_daemon())
    await asyncio.sleep(0)
    async with server:
        await server.serve_forever()
