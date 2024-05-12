#!/usr/bin/env python3


import cowsay as cs
import shlex
import cmd
import sys
import socket
import asyncio
import threading
import readline
from typing import TypeAlias
from collections.abc import Mapping
from io import StringIO


WEAPONS = {
    "sword": 10,
    "spear": 15,
    "axe": 20,
}

cust_mstr = cs.read_dot_cow(
    StringIO(
        """
$the_cow = <<EOC;
         $thoughts
          $thoughts
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\'--'//__
         (((""`  `"")))
EOC
"""
    )
)

list_cows = cs.list_cows() + ["jgsbat"]


class Game(cmd.Cmd):
    """
    MOOD client cmd line
    """

    def __init__(self, socket):
        super().__init__()
        self._socket = socket

    def do_addmon(self, args):
        """
        Adds a monster to the field with the specified name, greeting, hitpoints, and coordinates.

        :param monster_name: (str) The name of the monster. Must be one of the allowed monsters in the list 'allow_monsters'.
        :param hello: (str) The greeting string that the monster outputs.
        :param hp: (int) The hitpoints of the monster.
        :param coords: (tuple) The coordinates of the monster on the field in the format (x, y).
        :return: None
        """

        if len(args := shlex.split(args)) == 8 and args[0] in list_cows:
            msg = "addmon " + shlex.join(args)
            self._socket.send((msg.strip() + "\n").encode())
        elif args[0] not in list_cows:
            print("Cannot add unknown monster")
        else:
            print("Invalid arguments")

    def do_up(self, args):
        """
        Moves the player up 1 cell.

        :return: None
        """
        self._socket.send(("up\n").encode())

    def do_down(self, args):
        """
        Moves the player down 1 cell.

        :return: None
        """
        self._socket.send(("down\n").encode())

    def do_left(self, args):
        """
        Moves the player left 1 cell.

        :return: None
        """
        self._socket.send(("left\n").encode())

    def do_right(self, args):
        """
        Moves the player right 1 cell.

        :return: None
        """
        self._socket.send(("right\n").encode())

    def do_attack(self, args):
        """
        Attacks the specified monster with the standard attack, which inflicts 10 points of damage.

        :param name: (str) The name of the monster. Must be one of the allowed monsters in the list 'allow_monsters'.
        :param weapon: (str) The weapon to use for the attack.
        :return: None
        """

        match args := shlex.split(args):
            case [t, "with", weapon]:
                if weapon in WEAPONS:
                    self._socket.send(
                        (" ".join(["attack", t, str(WEAPONS[weapon])]) + "\n").encode()
                    )
                else:
                    print("Unknown weapon")
            case [t]:
                self._socket.send(
                    (" ".join(["attack", t, str(WEAPONS["sword"])]) + "\n").encode()
                )
            case _:
                print("Invalid arguments")

    def do_sayall(self, args):
        """
        Sends a message to all players.

        :param message: (str) The text of the message to send.

        :return: None
        """
        message = "sayall " + args + "\n"
        self._socket.send(message.encode())

    def do_quit(self, args):
        """
        Disconnect from the server.

            :return: None
        """
        self._socket.send("quit\n".encode())
        self.onecmd("exit")

    def do_exit(self, args):
        """
        Stop cmd line.

        :return: None
        """

        return 1


def get_reponse(_socket):
    while True:
        ans = _socket.recv(2048).decode()
        if ans:
            if ans.strip() == "Goodbye":
                break

            print("\n" + ans + "\n")
            print(
                f"\n{cmdline.prompt}{readline.get_line_buffer()}",
                end="",
                flush=True,
            )


def start(_socket):
    print("<<< Welcome to Python-MUD 0.1 >>>")
    print("Active session:")
    print(_socket.recv(1024).decode())

    global cmdline
    cmdline = Game(_socket)
    gm = threading.Thread(target=get_reponse, args=(_socket,))
    gm.start()
    Game(_socket).cmdloop()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
        _socket.connect(("localhost", 1338))
        _socket.send(f"{sys.argv[1]}\n".encode())
        start(_socket)
