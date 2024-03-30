import socket
import threading
import cmd
import cowsay
import shlex
import sys
import io

class Server:
    def __init__(self, host='localhost', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(1)
        self.clients = []
        self.game_state = GameState()
        self.connected_clients = {}

    def start(self):
        print("Server started")
        while True:
            client, addr = self.server.accept()
            print(f"Connected by {addr}")
            username = client.recv(1024).decode()  
            threading.Thread(target=self.handle_client, args=(client, username)).start()

    def broadcast_message(self, message):
        for client in self.connected_clients.values():
            client.sendall(message.encode())

    def attack_monster(self, attacker_username, weapon, monster_name, damage, remaining_hp, monster_killed):
        # Construct the message based on the attack event
        if monster_killed:
            message = f"{attacker_username} attacked {monster_name} with {weapon}, dealt {damage} damage, and killed the monster!"
        else:
            message = f"{attacker_username} attacked {monster_name} with {weapon}, dealt {damage} damage. Remaining HP: {remaining_hp}"

        self.broadcast_message(message)

    def add_monster(self, placer_username, monster_name, hp):
        message = f"{placer_username} added a {monster_name} with {hp} HP"
        self.broadcast_message(message)

    def user_entered(self, username):
        message = f"{username} entered the game"
        self.broadcast_message(message)

    def user_left(self, username):
        message = f"{username} left the game"
        self.broadcast_message(message)

    def handle_client(self, client, username):
        if username in self.connected_clients:
            client.sendall("Username already in use, please choose another one".encode())
            client.close()
        else:
            self.connected_clients[username] = client
            client.sendall("Connected to the server".encode())

        while True:
            data = client.recv(1024)
            if not data:
                break
            command, *args = data.decode().split()
            if command == 'move':
                dx, dy = map(int, args)
                response = self.game_state.move(dx, dy)
                client.sendall(response.encode())
            elif command == 'addmon':
                name, x, y, hello, hp = args
                response = self.game_state.addmon(name, int(x), int(y), hello, int(hp))
                self.add_monster(username, name, hp)  # Notify all clients about the monster addition event
                client.sendall(response.encode())
            elif command == 'attack':
                response = self.game_state.attack(self.game_state.player_pos, args[0])
                self.attack_monster(username, args[0], args[1], response.damage_dealt, response.remaining_hp, response.monster_killed)  # Notify all clients about the attack event
                client.sendall(response.encode())
            else:
                client.sendall("Unknown command".encode())

    

    def execute_command(self, command, args):
        if command == 'move':
            dx, dy = map(int, args)
            return self.game_state.move(dx, dy)
        elif command == 'addmon':
            name, x, y, hello, hp = args
            return self.game_state.addmon(name, int(x), int(y), hello, int(hp))
        elif command == 'attack':
            weapon = args[0]
            return self.game_state.attack(weapon)
        else:
            return "Unknown command"


class GameState:
    def __init__(self):
        self.squares = [[0 for _ in range(10)] for _ in range(10)]  
        self.player_pos = (0, 0)  
        self.monsters = {}  

    def move(self, dx, dy):
        new_x = (self.player_pos[0] + dx) % 10
        new_y = (self.player_pos[1] + dy) % 10
        if (new_x, new_y) in self.monsters:
            monster = self.monsters[(new_x, new_y)]
            return f"Player moved to position ({new_x}, {new_y})\n{monster.get_message()}"
        else:
            self.player_pos = (new_x, new_y)
            return f"Player moved to position ({new_x}, {new_y})"

    def addmon(self, name, x, y, hello, hp):
        if self.monsters.get((x, y)) is not None:
            print("Replaced the old monster")

        if name in cowsay.list_cows() + ["jgsbat"]:
            self.monsters[(x, y)] = Monster(name, hello, hp)
            print(f"Added monster {name} to ({x}, {y}) saying {hello} hp {int(hp)}")
            return "Added monster"  
        else:
            print("Cannot add unknown monster")
            return "Cannot add unknown monster"


    def attack(self, player_pos, weapon):
        player_x, player_y = player_pos
        for pos, monster in self.monsters.items():
            monster_x, monster_y = pos
            if (player_x, player_y) == (monster_x, monster_y):
                if weapon == "sword":
                    damage = 10
                elif weapon == "spear":
                    damage = 15
                elif weapon == "axe":
                    damage = 20
                else:
                    return "Unknown weapon"

                monster.hp -= damage
                if monster.hp <= 0:
                    del self.monsters[pos]
                    return f"Monster {monster.name} killed"
                else:
                    return f"Monster {monster.name} took damage, remaining health: {monster.hp} points"
        return "No monster here"


class Monster:
    def __init__(self, name, hello, hp):
        self.hello = hello
        self.name = name
        self.hp = int(hp) 

    def say(self):
        if self.name == "jgsbat":
            print(cowsay.cowsay(self.hello, cowfile=custom_monster))
        else:
            print(cowsay.cowsay(self.hello, cow=self.name))

    def get_message(self):
        if self.name == "jgsbat":
            return cowsay.cowsay(self.hello, cowfile=custom_monster)
        else:
            return cowsay.cowsay(self.hello, cow=self.name)

    
server = Server()
server.start()

