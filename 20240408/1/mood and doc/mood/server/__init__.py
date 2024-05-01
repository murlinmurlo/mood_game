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



import asyncio
import cowsay
import random
import shlex
from ..common import get_custom_cow, get_list_custom_cows, FIELD_SIZE, arsenal


field = [[None]*FIELD_SIZE for _ in range(FIELD_SIZE)]
logged_users = {}


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


async def send_all_users(message):
    """Send message to all users."""
    global logged_users
    for gamer in logged_users.values():
        await gamer.queue.put(message)


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
    await gamer.queue.put(f"Moved to ({gamer.x}, {gamer.y})\n")
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
    new_message = f"{login} added monster {name} with {hp}hp to ({x}, {y}) saying '{message}'\n"
    if field[y][x] is not None:
        new_message += "Replaced the old monster\n"
    field[y][x] = Monster(name=name, message=message, hp=hp)
    await send_all_users(new_message)


async def attack(name, weapon, login):
    """Execute command ``attack``.

    :param name: attacked monster's name
    :param weapon: user's weapon
    :param login: login of user that call ``attack``
    """
    global logged_users
    gamer = logged_users[login]
    if field[gamer.y][gamer.x] is None or field[gamer.y][gamer.x].name != name:
        await gamer.queue.put(f'No {name} here')
        return
    monster = field[gamer.y][gamer.x]
    damage = arsenal[weapon]
    damage = damage if monster.hp >= damage else monster.hp
    new_message = f'{login} attacked {monster.name} with {weapon}, damage {damage}hp\n'
    monster.hp -= damage
    if monster.hp == 0:
        new_message += f'{monster.name} died\n'
        field[gamer.y][gamer.x] = None
    else:
        new_message += f'{monster.name} now has {monster.hp}\n'
    await send_all_users(new_message)


async def sayall(message, login):
    """Execute command ``sayall``.

    :param message: sended to all user message
    :param login: login of user that call ``sayall``
    """
    new_message = f"{login}: {message}\n"
    await send_all_users(new_message)


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
    await send_all_users(f"User '{login}' logged in\n")

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
            case ['quit']:
                send.cancel()
                receive.cancel()
                del logged_users[login]
                writer.write('Quit\n'.encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                await send_all_users(f"User '{login}' logged out\n")
                flag_quit = True
                return
            case _:
                print(f'Unknown command {cmd}')
                send.cancel()
                receive.cancel()
                del logged_users[login]
                writer.write('Quit\n'.encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
                await send_all_users(f"User '{login}' logged out\n")
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
            await send_all_users(f"{monster.name} moved one cell {shift_direction}\n")
            await monster_encounter(new_y, new_x)
            return


async def wandering_monster():
    """Move monster while server is running."""
    while True:
        await asyncio.sleep(30)
        print("Run random choice")
        await random_choice_monster()


async def run_server():
    """Server run coroutine."""
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()


async def main():
    """Execute ``run_server`` and ``wandering_monster`` coroutine."""
    await asyncio.gather(run_server(), wandering_monster())
