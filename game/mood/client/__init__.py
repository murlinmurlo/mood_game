"""This module contains methods that are dedicated to managing and facilitating client-side operations."""

import socket
import readline
import shlex
import cmd
import time
import threading
import webbrowser
from ..common import (get_weapons,
                      FIELD_SIZE,
                      READ_FROM_FILE_TIMEOUT)
from pathlib import Path


prompt = "~ "
doc_path = str(Path(__file__).parents[1] / 'docs/build/html/index.html')


class MUD_shell(cmd.Cmd):
    """This class inherits from `cmd.Cmd` and is responsible for parsing and processing user commands, facilitating user interaction with the system."""

    def __init__(self, socket, timeout=0, *args, **kwargs):
        """This method initializes the MUD_shell object, setting up the necessary properties such as the socket and timeout values for efficient functioning."""
        self.socket = socket
        self.timeout = timeout
        self.prompt = ""
        super().__init__(*args, **kwargs)

    def precmd(self, line):
        """Pause the operation if data is being read from a file to prevent overloading the server with too many requests at once."""
        time.sleep(self.timeout)
        return super().precmd(line)

    def do_up(self, arg):
        """This method processes the 'up' command, executing the necessary actions associated with the command."""
        self.socket.sendall("move 0 -1\n".encode())

    def do_down(self, arg):
        """This method processes the 'down' command, executing the necessary actions associated with the command."""
        self.socket.sendall("move 0 1\n".encode())

    def do_left(self, arg):
        """This method processes the 'left' command, executing the necessary actions associated with the command."""
        self.socket.sendall("move -1 0\n".encode())

    def do_right(self, arg):
        """This method processes the 'right' command, executing the necessary actions associated with the command."""
        self.socket.sendall("move 1 0 \n".encode())

    def do_addmon(self, arg):
        """
        This method processes the 'addmon' command and verifies the correctness of the provided arguments to ensure they are valid and suitable for further use.
        """
        options = shlex.split(arg)
        if len(options) != 8:
            print(f"Invalid arguments amount\n{prompt}", end='')
            return
        param_dict = {}
        param_dict['name'] = options[0]
        opt_set = set()
        i = 1
        err_flag = False
        while i < len(options):                                          
            match options[i]:
                case 'hello':
                    param_dict['phrase'] = shlex.quote(options[i+1])
                    opt_set.add('hello')
                    i += 2
                case 'hp':
                    try:
                        hp = int(options[i+1])
                    except Exception:
                        print(f"Invalid hp\n{prompt}", end='')
                        err_flag = True
                        break
                    if not (hp > 0):
                        print(f"Invalid hp\n{prompt}", end='')
                        err_flag = True
                        break
                    param_dict['hp'] = hp
                    opt_set.add('hp')
                    i += 2
                case 'coords':
                    try:
                        x = int(options[i+1])
                        y = int(options[i+2])
                    except Exception:
                        print(f"Invalid coords\n{prompt}", end='')
                        err_flag = True
                        break
                    if not (0 <= x <= FIELD_SIZE and 0 <= y <= FIELD_SIZE):
                        print(f"Invalid coords\n{prompt}", end='')
                        err_flag = True
                        break
                    opt_set.add('coords')
                    param_dict['coords_x'] = x
                    param_dict['coords_y'] = y
                    i += 3
                case _:
                    print(f"Invalid arguments\n{prompt}", end='')
                    err_flag = True
                    return
        if err_flag:
            return
        if opt_set != {'hello', 'hp', 'coords'}:
            print(f"Missing required arguments\n{prompt}", end='')
            return
        opts = 'addmon'
        for opt in 'name', 'coords_x', 'coords_y', 'phrase', 'hp':
            opts += ' ' + str(param_dict[opt])
        self.socket.sendall((opts+'\n').encode())

    def do_attack(self, arg):
        """This method is responsible for processing the 'attack' command, managing the necessary operations associated with the attack functionality."""
        arg = shlex.split(arg)
        if len(arg) == 1:
            weapon = "sword"
        elif len(arg) == 3:
            match arg[1:]:
                case ['with', arms]:
                    if arms not in get_weapons():
                        print(f"Unknown weapon\n{prompt}", end='')
                        return
                    else:
                        weapon = arms
                case _:
                    print(f"Unknown arguments\n{prompt}", end='')
                    return
        else:
            print(f"Unknown arguments\n{prompt}", end='')
            return
        self.socket.sendall(f"attack {arg[0]} {weapon}\n".encode())

    def do_sayall(self, arg):
        """This method processes the 'sayall' command, executing the necessary actions associated with the command."""
        self.socket.sendall(f"sayall {arg}\n".encode())

    def do_movemonsters(self, arg):
        """This method processes the 'movemonsters' command, executing the necessary actions associated with the command."""
        match arg:
            case 'on':
                msg = "movemonsters on"
                self.socket.sendall((msg + '\n').encode())
            case 'off':
                msg = "movemonsters off"
                self.socket.sendall((msg + '\n').encode())
            case _:
                print(f"Invalid arguments\n{prompt}", end='')

    def do_locale(self, arg):
        """This method processes the 'locale' command, executing the necessary actions associated with the command."""
        self.socket.sendall(f"locale {arg}\n".encode())
        print(prompt, end="")

    def do_documentation(self, arg):
        """This method opens the generated documentation in the default web browser, providing the user with necessary information and guidelines."""
        webbrowser.open(doc_path)

    def do_EOF(self, arg):
        """This method checks for the End Of File (EOF) marker, and if it is encountered, the method returns a value of 1."""
        return 1

    def emptyline(self):
        """This method checks for an empty line, and if such a line is encountered, the method doesn't perform any operation."""
        pass


def is_socket_closed(sock: socket.socket) -> bool:
    """
    This method checks the status of the socket connection. It determines whether the socket is closed or still open for communication.

    :param sock: socket to check it's availability
    :type sock: :class:`socket.socket`
    """
    try:
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError:
        return False
    except ConnectionResetError:
        return True
    except Exception as e:
        return False
    return False


def msg_reciever(socket, prompt):
    """
    This method is designed to receive a message through the socket, and then output the received message to the user.

    If user starts writing input but didn't press enter,
    output this input after a message

    :param socket: socket to listen on
    :param prompt: print this prompt after the message
    :type socket: :class:`socket.socket`
    :type prompt: str
    """
    while True:
        if is_socket_closed(socket):
            print("Server is down")
            quit(1)
            break
        try:
            msg = socket.recv(1024).decode()
        except Exception as e:
            print("Socket is now closed\nExiting...")
            quit()
        buf = readline.get_line_buffer()
        if buf:
            print(f"\n{msg}\n{prompt}{buf}", end="",
                  flush=True)
        else:
            print('', end='\033[2K\033[1G')
            print(f"{msg}\n{prompt}{buf}", end="",
                  flush=True)


def start_client(login, in_file=None):
    """
    This method starts the client, it establishes a socket connection and initiates a client-side session. It can also handle input from a file.
    """
    host = "localhost"
    port = 1337

    from_file = True if in_file else False

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        msg_handler = threading.Thread(target=msg_reciever,
                                       args=(s, prompt))
        msg_handler.start()
        s.sendall((login + '\n').encode())
        if from_file:
            with open(in_file, 'r') as f:
                shell = MUD_shell(s, timeout=READ_FROM_FILE_TIMEOUT, stdin=f)
                shell.use_rawinput = False
                shell.cmdloop()
        else:
            shell = MUD_shell(s)
        shell.cmdloop()


    