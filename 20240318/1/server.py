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
    # Реализация класса GameState аналогична вашему классу Field, но с добавлением метода attack

server = Server()
server.start()

