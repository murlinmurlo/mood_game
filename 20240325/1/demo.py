import socket
import asyncio

class Client:
    def __init__(self, host='localhost', port=12345, username='guest'):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.username = username
        self.reader = None
        self.writer = None
        self.host = host
        self.port = port

    async def connect(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        self.reader = reader
        self.writer = writer
        self.writer.write(self.username.encode())
        await self.writer.drain()
        print("Connected to the server")

        asyncio.create_task(self.receive_messages()) 

    async def send_command(self, command):
        if self.writer:
            self.writer.write(command.encode())
            await self.writer.drain()
        else:
            print("Not connected to the server. Cannot send command.")
 
 

    async def receive_messages(self):
        while True:
            data = await self.reader.read(100)
            if not data:
                break
            print(data.decode())
        async def send_command(self, command):
            self.writer.write(command.encode())
            await self.writer.drain()

async def main():
    print("<<< Welcome to Python-MUD 0.1 >>>")
    username = input("Enter your username: ")
    client = Client(username=username)
    await client.connect()

    while True:
        command = input("> ")
        await client.send_command(command)

asyncio.run(main())
