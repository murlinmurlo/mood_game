"""
Server for MUD (multi user dangeon).

Server command:
  | ``move <x> <y>``                             (0 <= x < 10, 0 <= y < 10)
  | ``addmon <name> <x> <y> <message> <hp>``     (0 <= x < 10, 0 <= y < 10, 0 < hp)
  | ``attack <name> <weapon>``                   (weapon correct)
  | ``sayall <message>``
  | ``movemonsters on|off``
  | ``quit``
"""


import asyncio
import cowsay
import gettext
import random
import shlex
from ..common import get_custom_cow, get_list_custom_cows, FIELD_SIZE, arsenal


field = [[None]*FIELD_SIZE for _ in range(FIELD_SIZE)]
logged_users = {}
WANDERING_TIMEOUT = 30
LOCALES = {
    ("ru_RU.UTF-8"): gettext.translation("mood.server", "po", ["ru"]),
    ("en_US.UTF-8"): gettext.NullTranslations(),
}


def make_cowsay(name, message):
    """Make cowsay with cow with name `name` and message `message`."""
    if name in cowsay.list_cows():
        return cowsay.cowsay(message, cow=name)
    elif name in get_list_custom_cows():
        cow = get_custom_cow(name)
        return cowsay.cowsay(message, cowfile=cow)


class Gamer:
    """Info about logged in user.

    :param x: gamer's horizontal coordinate
    :param y: gamer's vertical coordinate
    :param queue: queue of server responce
    """

    def __init__(self, x=0, y=0):
        """Init gamer in cell (0, 0)."""
        self.x = x
        self.y = y
        self.queue = asyncio.Queue()
        self._locale = 'en_US.UTF-8'

    @property
    def locale(self):
        return self._locale

    @locale.setter
    def locale(self, new_locale):
        if new_locale in LOCALES.keys():
            self._locale = new_locale
        else:
            print(f"Locale '{new_locale}' not found. Set locale 'en_US.UTF-8'")
            self._locale = "en_US.UTF-8"


class Monster:
    """Info about added monster.

    :param name: monster name
    :param message: message that monster say
    :param hp: monster's health point
    """

    def __init__(self, name='default', message='hello', hp=0):
        """Init monster."""
        self.name = name
        self.message = message
        self.hp = hp

    def __str__(self):
        """Return monster name."""
        return self.name


async def send_all_users(message, format_args, num=None):
    """Send message to all users."""
    global logged_users
    for gamer in logged_users.values():
        # TODO l10n
        if num is None:
            await gamer.queue.put(LOCALES[gamer.locale].gettext(message).format(*format_args))
        else:
            await gamer.queue.put(LOCALES[gamer.locale].ngettext(message, message, num).format(*format_args))


async def encounter(y, x, login):
    """Send to client monster's greetings.

    :param y: vertical coordinate
    :param x: horizontal coordinate
    :param login: login of user that triggered encounter
    """
    global field, logged_users
    gamer = logged_users[login]
    if field[y][x] is None:
        return
    message = make_cowsay(field[y][x].name, field[y][x].message) + '\n'
    await gamer.queue.put(message)


async def move(x, y, login):
    """Execute command ``move``.

    :param x: horizontal shift
    :param y: vertical shift
    :param login: login of user that call ``move``
    """
    global logged_users
    gamer = logged_users[login]
    gamer.x = (gamer.x + x) % FIELD_SIZE
    gamer.y = (gamer.y + y) % FIELD_SIZE
    # TODO l10n
    await gamer.queue.put(LOCALES[logged_users[login].locale].gettext('Moved to ({}, {})\n').format(gamer.x, gamer.y))
    await encounter(gamer.y, gamer.x, login)


async def addmon(name, x, y, message, hp, login):
    """Execute command ``addmon``.

    :param name: monster name
    :param x: horizontal monster's coordinate
    :param y: vertical monster's coordinate
    :param message: message that monster say
    :param hp: monster's health point
    :param login: login of user that call ``addmon``
    """
    new_message = "{} added monster {} with {}hp to ({}, {}) saying '{}'\n"
    format_args = [login, name, hp, x, y, message]
    if field[y][x] is not None:
        new_message += "Replaced the old monster\n"
    field[y][x] = Monster(name=name, message=message, hp=hp)
    # TODO l10n
    await send_all_users(new_message, format_args, hp)


async def attack(name, weapon, login):
    """Execute command ``attack``.

    :param name: attacked monster's name
    :param weapon: user's weapon
    :param login: login of user that call ``attack``
    """
    global logged_users
    gamer = logged_users[login]
    if field[gamer.y][gamer.x] is None or field[gamer.y][gamer.x].name != name:
        # TODO l10n
        await gamer.queue.put(LOCALES[logged_users[login].locale].gettext('No {} here\n').format(name))
        return
    monster = field[gamer.y][gamer.x]
    damage = arsenal[weapon]
    damage = damage if monster.hp >= damage else monster.hp
    new_message_1 = f'{{}} attacked {{}} with {weapon}, damage {{}}hp\n'
    format_args_1 = [login, monster.name, damage]
    monster.hp -= damage
    if monster.hp == 0:
        new_message_2 = '{} died\n'
        format_args_2 = [monster.name]
        field[gamer.y][gamer.x] = None
        await send_all_users(new_message_1, format_args_1, damage)
        await send_all_users(new_message_2, format_args_2)
    else:
        new_message_2 = '{} now has {}hp\n'
        format_args_2 = [monster.name, monster.hp]
        await send_all_users(new_message_1, format_args_1, damage)
        await send_all_users(new_message_2, format_args_2, monster.hp)


async def sayall(message, login):
    """Execute command ``sayall``.

    :param message: sended to all user message
    :param login: login of user that call ``sayall``
    """
    new_message = "{}: {}\n"
    format_args = [login, message]
    await send_all_users(new_message, format_args)


async def movemonsters(state):
    """Execute command ``movemonsters``.

    :param state: on or off state
    """
    global wandering_monster_task
    if state == 'on':
        if wandering_monster_task.cancelled():
            wandering_monster_task = asyncio.create_task(wandering_monster())
    # TODO l10n
        await send_all_users('Moving monsters: on\n', [])
    else:
        if not wandering_monster_task.cancelled():
            wandering_monster_task.cancel()
    # TODO l10n
        await send_all_users('Moving monsters: off\n', [])


async def locale(new_locale, login):
    """Execute command ``locale``.
    If new locale is not en_US.UTF-8 or ru_RU.UTF-8, then set en_US.UTF-8.

    :param new_locale: new locale (en_US.UTF-8 or ru_RU.UTF-8)
    """
    global logged_users
    gamer = logged_users[login]
    gamer.locale = new_locale
    await gamer.queue.put(
            LOCALES[gamer.locale].gettext("Set up locale: {}").format(gamer.locale)
            )


async def chat(reader, writer):
    """Parce and execute command and send responce to client."""
    global logged_users, field

    login = await reader.readline()
    login = login.decode().strip()
    if login in logged_users.keys():
        writer.write(f"0User '{login}' already logged in\nConnection close\n".encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return

    logged_users[login] = Gamer()
    writer.write(f"1Success! You are logged in as '{login}'\n".encode())
    await writer.drain()
    # TODO l10n
    await send_all_users("User '{}' logged in\n", [login])

    async def parce_command(cmd):
        nonlocal reader, writer, send, receive, flag_quit
        print(cmd)
        print(cmd.decode().strip())
        cmd = shlex.split(cmd.decode().strip())
        print(cmd)
        match cmd:
            case ['move', x, y]:
                await move(int(x), int(y), login)
            case ['addmon', name, x, y, message, hp]:
                await addmon(name, int(x), int(y), message, int(hp), login)
            case ['attack', name, weapon]:
                await attack(name, weapon, login)
            case ['sayall', message]:
                await sayall(message, login)
            case ['movemonsters', state]:
                await movemonsters(state)
            case ['locale', new_locale]:
                await locale(new_locale, login)
            case ['quit']:
                send.cancel()
                receive.cancel()
                del logged_users[login]
                # TODO l10n
                writer.write('Quit\n'.encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                # TODO l10n
                await send_all_users("User '{}' logged out\n", [login])
                flag_quit = True
                return
            case _:
                print(f'Unknown command {cmd}')
                send.cancel()
                receive.cancel()
                del logged_users[login]
                # TODO l10n
                writer.write('Quit\n'.encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                # TODO l10n
                await send_all_users("User '{}' logged out\n", [login])
                flag_quit = True
                return

    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(logged_users[login].queue.get())
    flag_quit = False
    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())
                cmd = q.result()
                await parce_command(cmd)
                if flag_quit:
                    break
            elif q is receive:
                # Maybe need try except KeyError
                receive = asyncio.create_task(logged_users[login].queue.get())
                writer.write(f"{q.result()}\n".encode())
                await writer.drain()
        if flag_quit:
            break


async def monster_encounter(y, x):
    """Encounter called by random_choice_monster.

    :param x: monster's horizontal coordinate
    :param y: monster's vertical coordinate
    """
    global field, logged_users
    for gamer in logged_users.values():
        if gamer.x == x and gamer.y == y:
            message = make_cowsay(field[y][x].name, field[y][x].message) + '\n'
            await gamer.queue.put(message)


async def random_choice_monster():
    """Choice random monster and try to move it."""
    global field
    while True:
        monster_coords = [(y, x) for y in range(FIELD_SIZE) for x in range(FIELD_SIZE)
                          if field[y][x]]
        if not monster_coords:
            return
        y, x = random.choice(monster_coords)
        shift_direction, shift_y, shift_x = random.choice(
                [('right', 0, 1),
                 ('left', 0, -1),
                 ('down', 1, 0),
                 ('up', -1, 0)]
                )
        new_y, new_x = (y + shift_y) % FIELD_SIZE, (x + shift_x) % FIELD_SIZE
        if not field[new_y][new_x]:
            monster = field[y][x]
            field[new_y][new_x] = monster
            field[y][x] = None
            # TODO l10n
            await send_all_users(f"{{}} moved one cell {shift_direction}\n", [monster.name])
            await monster_encounter(new_y, new_x)
            return


async def wandering_monster():
    """Move monster while server is running."""
    while True:
        await asyncio.sleep(WANDERING_TIMEOUT)
        print("Run random choice")
        await random_choice_monster()


async def run_server():
    """Server run coroutine."""


async def main():
    """Execute ``run_server`` and ``wandering_monster`` coroutine."""
    global wandering_monster_task
    wandering_monster_task = asyncio.create_task(wandering_monster())
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()
    # asyncio.run(run_server())
    # await asyncio.gather(run_server(), wandering_monster())
