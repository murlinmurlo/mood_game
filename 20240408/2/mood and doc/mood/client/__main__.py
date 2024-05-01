import argparse
import cmd
import readline
import socket
import shlex
import sys
import time
import threading
import typing
from ..common import get_extended_list_cows, FIELD_SIZE, arsenal


class InvalidArgument(Exception):
    """Invalid argument when parsing command."""

    pass


def move(direction, arg, socket):
    """Correctness checker for 'up', 'down', 'right' and 'left' command."""
    if arg:
        print(f"Unexpected argument '{arg}'")
        return
    match direction:
        case 'up':
            cmd = "move 0 -1\n"
        case 'down':
            cmd = "move 0 1\n"
        case 'left':
            cmd = "move -1 0\n"
        case 'right':
            cmd = "move 1 0\n"
        case _:
            print('Incorrect direction')
            return
    socket.sendall(cmd.encode())


def check_hp(hp_str: str) -> int:
    """Correctness checker for 'hp' argument in 'addmon' command."""
    try:
        hp = int(hp_str)
    except ValueError:
        print('hp must be int')
        raise InvalidArgument()
    if hp < 0:
        print('hp must be more that 0')
        raise InvalidArgument()
    return hp


def check_coords(x_str: str, y_str: str) -> typing.Tuple[int, int]:
    """Correctness checker for 'coords' argument in 'addmon' command."""
    try:
        x, y = int(x_str), int(y_str)
    except ValueError:
        print('coords must be int')
        raise InvalidArgument
    if x < 0 or x >= FIELD_SIZE or y < 0 or y >= FIELD_SIZE:
        print("Invalid coords")
        raise InvalidArgument
    return x, y


def check_addmon_name(name: str) -> str:
    """Correctness checker for 'name' argument in 'addmon' command."""
    if name not in get_extended_list_cows():
        print('Unexpected cow')
        raise InvalidArgument
    return name


def addmon(arg, socket):
    """Correctness checker for 'addmon' command."""
    if not arg:
        print("Error! Empty arguments")
        return
    args = shlex.split(arg)
    params = {'name': None,
              'hello': None,
              'coords': None,
              'hp': None}
    params['name'] = args[0]
    i = 1
    while i < len(args):
        match args[i]:
            case 'hello' | 'hp' as par:
                i += 1
                try:
                    params[par] = args[i]
                except IndexError:
                    print('Index out of range')
                    return
            case 'coords' as par:
                i += 1
                try:
                    params[par] = (args[i], args[i + 1])
                    i += 1
                except IndexError:
                    print('Index out of range')
                    return
            case _:
                print(f'Unexpected arg: {args[i]}')
                return
        i += 1

    if any([p is None for p in params.values()]):
        print('Missing required argument')
        return

    try:
        name = check_addmon_name(params['name'])
        hello = params['hello']
        x, y = check_coords(*params['coords'])
        hp = check_hp(params['hp'])
    except InvalidArgument:
        print("Invalid argument")
        return
    param_str = shlex.join(list(map(str, [name, x, y, hello, hp])))
    socket.sendall(f"addmon {param_str}\n".encode())


def check_attack_name(name: str) -> str:
    """Correctness checker for 'name' argument in 'attack' command."""
    if name == '':
        print("Missing required argument: name")
        raise InvalidArgument
    list_name = shlex.split(name)
    if len(list_name) > 1:
        print(f'Unexpected args: {name[1:]}')
        raise InvalidArgument
    return list_name[0]


def check_weapon(weapon: str) -> str:
    """Correctness checker for 'weapon' argument in 'attack' command."""
    if weapon not in arsenal.keys():
        print('Unknown weapon')
        raise InvalidArgument
    return weapon


def attack(arg, socket):
    """Correctness checker for 'attack' command."""
    if not arg:
        print("Error! Empty arguments")
        return
    args = shlex.split(arg)
    try:
        name = check_attack_name(args[0])
    except InvalidArgument:
        return
    i = 1
    weapon = 'sword'
    while i < len(args):
        match args[i]:
            case 'with':
                i += 1
                try:
                    weapon = args[i]
                except IndexError:
                    print('Index out of range')
                    return
            case _:
                print(f'Unexpected arg: {args[i]}')
                return
        i += 1
    try:
        weapon = check_weapon(weapon)
    except InvalidArgument:
        return
    socket.sendall(f"attack {name} {weapon}\n".encode())


def sayall(arg, socket):
    """Correctness checker for 'sayall' command."""
    if not arg:
        print("Error! Empty arguments")
        return
    message = shlex.split(arg)
    if len(message) > 1:
        print(f"Too many arguments - {len(message)}. Expected 1")
        return
    message = shlex.join(["sayall", message[0]])
    socket.sendall(f"{message}\n".encode())


def quit(socket):
    """Quit command."""
    socket.sendall("quit\n".encode())


class MUDcmd(cmd.Cmd):
    """Multi User Dangeon commandline."""

    prompt = ">> "

    def __init__(self, socket, timeout=0, *args, **kwargs):
        """Init from class cmd.Cmd."""
        super().__init__(*args, **kwargs)
        self.socket = socket
        self.timeout = timeout

    def precmd(self, line):
        """Run before command execution."""
        time.sleep(self.timeout)
        return super().precmd(line)

    def emptyline(self):
        """Empty line interpted as 'do nothing'."""
        pass

    def do_up(self, arg):
        """Move gamer up."""
        move('up', arg, self.socket)

    def do_down(self, arg):
        """Move gamer down."""
        move('down', arg, self.socket)

    def do_left(self, arg):
        """Move gamer left."""
        move('left', arg, self.socket)

    def do_right(self, arg):
        """Move gamer right."""
        move('right', arg, self.socket)

    def do_addmon(self, arg):
        """Add monster.

        addmon
            name - monster name
            hello <message> - message that monster say
            coords <x> <y> - monster's coords
            hp <hp> - monster's health point
        """
        addmon(arg, self.socket)

    def complete_addmon(self, text, line, begidx, endidx):
        """Complete command addmon."""
        params = {'hello', 'hp', 'coords'}
        cmd_len = len(shlex.split(line[:endidx] + '.'))
        if cmd_len == 2:
            # Name
            return [c for c in get_extended_list_cows() if c.startswith(text)]
        else:
            # Other params
            return [c for c in params if c.startswith(text)]

    def do_attack(self, arg):
        """Attack monster in current cell.

        attack <monster> [with <weapon>] (default weapon is sword)
        """
        attack(arg, self.socket)

    def complete_attack(self, text, line, begidx, endidx):
        """Complete command attack."""
        cmd_len = len(shlex.split(line[:endidx] + '.'))
        if cmd_len == 2:
            return [c for c in get_extended_list_cows() if c.startswith(text)]
        elif shlex.split(line[:endidx] + '.')[-2] == 'with':
            return [c for c in arsenal.keys() if c.startswith(text)]
        else:
            return ['with']

    def do_sayall(self, arg):
        """Send message to all logged users.

        sayall <message>
        """
        sayall(arg, self.socket)

    def do_quit(self, arg):
        """Quit and finish program."""
        quit(self.socket)
        return 1

    def do_EOF(self, arg):
        """Quit and finish program."""
        quit(self.socket)
        return 1


def print_srv_message(socket, stop_event, cmdline):
    """Print message from server while stop_event is not set."""
    time.sleep(0.1)
    while not stop_event.wait(0):

        response = socket.recv(8192).decode().strip()
        print(f"\n{response}")
        print(f"{cmdline.prompt}{readline.get_line_buffer()}", end="", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='MOOD',
                                     description='Client for MOOD (multi user dangeon)')
    parser.add_argument('login')
    parser.add_argument('--file', metavar='filename')
    args = parser.parse_args()
    print("<<< Welcome to Python-MUD 0.1 >>>")
    host, port = "localhost", 1337
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        soc.connect((host, port))
        login = args.login
        soc.sendall(f'{login}\n'.encode())
        login_resp = soc.recv(8192).decode().strip()
        if login_resp[0] == '0':
            print(login_resp[1:])
            sys.exit(0)
        elif login_resp[0] == '1':
            print(login_resp[1:])

        if args.file is None:
            # Default start cmd
            cmdline = MUDcmd(soc)
            stop_event = threading.Event()
            printer = threading.Thread(target=print_srv_message,
                                       args=(soc, stop_event, cmdline)
                                       )
            printer.start()
            cmdline.cmdloop()
            stop_event.set()
            printer.join()
        else:
            # Read command from file
            with open(args.file) as mood_file:
                cmdline = MUDcmd(soc, timeout=1, stdin=mood_file)
                cmdline.prompt = ''
                cmdline.use_rawinput = False
                stop_event = threading.Event()
                printer = threading.Thread(target=print_srv_message,
                                           args=(soc, stop_event, cmdline)
                                           )
                printer.start()
                cmdline.cmdloop()
                stop_event.set()
                printer.join()
