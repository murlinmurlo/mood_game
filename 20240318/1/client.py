import socket

class Client:
    def __init__(self, host='localhost', port=12345):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

    def send_command(self, command):
        self.client.sendall(command.encode())
        data = self.client.recv(1024)
        print(data.decode())

    def start(self):
        while True:
            command = input("> ")
            self.send_command(command)

client = Client()
client.start()

