import socket
import sys

host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])

def handle_command(command, conn):
    if command.startswith("print"):
        words = command.split(" ")[1:]
        output = " ".join(words)
        conn.sendall(output.encode())
    elif command.startswith("info"):
        info_type = command.split(" ")[1]
        if info_type == "host":
            conn.sendall(str(conn.getpeername()[0]).encode())
        elif info_type == "port":
            conn.sendall(str(conn.getpeername()[1]).encode())
        else:
            conn.sendall("Invalid info type".encode())
    else:
        conn.sendall("Invalid command".encode())

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            command = data.decode()
            handle_command(command, conn)
