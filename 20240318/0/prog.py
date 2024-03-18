import sys
import socket
import cmd

class Netcat(cmd.Cmd):
    prompt = "~"

    def do_send(self, arg):
        """Send a message to the server"""
        host = "localhost" if len(sys.argv) < 2 else sys.argv[1]
        port = 1337 if len(sys.argv) < 3 else int(sys.argv[2])
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(arg.encode())
            print(s.recv(1024).decode())

if __name__ == "__main__":
    Netcat().cmdloop()
