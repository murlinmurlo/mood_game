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
        print("Server started")
        while True:
            client, addr = self.server.accept()
            print(f"Connected by {addr}")
            username = client.recv(1024).decode()  # Receive the username from the client
            threading.Thread(target=self.handle_client, args=(client, username)).start()

print("<<< Welcome to Python-MUD 0.1 >>>")
username = input("Enter your username: ")
client = Client(username=username)
client.start()
