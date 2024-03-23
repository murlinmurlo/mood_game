import socket
import threading

class Server:
    def __init__(self, host='localhost', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(1)
        self.clients = []
        self.game_state = GameState()

    def start(self):
        print("Server started")
        while True:
            client, addr = self.server.accept()
            print(f"Connected by {addr}")
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        while True:
            data = client.recv(1024)
            if not data:
                break
            command, *args = data.decode().split()
            response = self.execute_command(command, args)
            client.sendall(response.encode())

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

import socket
import threading

class Server:
    def __init__(self, host='localhost', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(1)
        self.clients = []
        self.game_state = GameState()

    def start(self):
        print("Server started")
        while True:
            client, addr = self.server.accept()
            print(f"Connected by {addr}")
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        while True:
            data = client.recv(1024)
            if not data:
                break
            command, *args = data.decode().split()
            response = self.execute_command(command, args)
            client.sendall(response.encode())

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
        self.player_pos = (new_x, new_y)
        return f"Player moved to position ({new_x}, {new_y})"

    def addmon(self, name, x, y, hello, hp):
        if self.matrix.get((x, y)) is not None:
            print("Replaced the old monster")

        if name in cowsay.list_cows() + ["jgsbat"]:
            self.matrix[(x, y)] = Monster(name, hello, hp)
            print(f"Added monster {name} to ({x}, {y}) saying {hello} hp {int(hp)}")
        else:
            print("Cannot add unknown monster")

    def attack(self, weapon):
        for pos, monster in self.monsters.items():
            if weapon == "sword":
                damage = 10
            elif weapon == "spear":
                damage = 15
            elif weapon == "axe":
                damage = 20
            else:
                return "Unknown weapon"

            monster['hp'] -= damage
            if monster['hp'] <= 0:
                del self.monsters[pos]
                return f"Monster {monster['name']} killed"
            else:
                return f"Monster {monster['name']} took damage, remaining health: {monster['hp']} points"
        return f"Monster not found"

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

    

    
server = Server()
server.start()

