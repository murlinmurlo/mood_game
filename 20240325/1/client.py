import socket

class Client:
    def __init__(self, host='localhost', port=12345, username='guest'):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.username = username

    def send_command(self, command):
        self.client.sendall(command.encode())
        data = self.client.recv(1024)
        print(data.decode())

    def start(self):
        self.client.sendall(self.username.encode())
        response = self.client.recv(1024).decode()
        print(response)
        if response != "Connected to the server":
            print("Connection failed: " + response)
            return
        while True:
            command = input("> ")
            self.send_command(command)

print("<<< Welcome to Python-MUD 0.1 >>>")
username = input("Enter your username: ")
client = Client(username=username)
client.start()
