import sys
import socket
import cmd
import cowsay
import threading
import time
import readline
import shlex

class clientCmd(cmd.Cmd):
	prompt = ">>"
	
	
	def __init__(self, socket):
		super().__init__()
		self.s = socket
		
	def do_EOF(self, line):
		self.s = None
		return 1
		
	def do_move(self, args):
		command = shlex.split(args)
		if len(command) != 2:
			print("Invalid arguments")
			return
		msg = "move " + command[0] + " " + command[1] + "\n"
		self.s.sendall(msg.encode())
	
	def do_addmon(self, args):
		command = shlex.split(args)
		if len(command) != 5:
			print("Invalid arguments")
			return
		
		msg = "addmon "
		for i in range(4):
			msg += command[i] + " "
		msg += command[4] + "\n"
		self.s.sendall(msg.encode())
		
	def do_attack(self, args):
		command = shlex.split(args)
		if len(command) == 1:
			msg = "attack " + command[0] + "\n"
		elif len(command) == 3 and command [1] == "with":
			msg = "attack " + command[0] + " with " + command[2] + "\n"
		else:
			print("Invalid arguments")
			return 
		self.s.sendall(msg.encode())
		
	
	def complete_attack(self, text, line, begidx, endidx):
        	weapons = ["sword", "spear", "axe"]
        	monster_names = cowsay.list_cows() + ["jgsbat"]
        	command = (line[:endidx]).split()
        	if "with" in command:
        	    return [weapon for weapon in weapons if weapon.startswith(text)]
        	else:
        	    return [name for name in monster_names if name.startswith(text)]
        	    

def getmsg(cmdline):
	while res := cmdline.s.recv(1024).rstrip().decode():
		print(f"{res}\n{cmdline.prompt}{readline.get_line_buffer()}", end="", flush=True)
        	    

username = sys.argv[1]
host = "localhost" if len(sys.argv) < 3 else sys.argv[2]
port = 1337 if len(sys.argv) < 4 else int(sys.argv[3])

if __name__ == "__main__":
	print("<<< Welcome to Python-MUD 0.1 >>>")
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect((host, port))
		s.sendall(f"{username}\n".encode())
		connection = s.recv(1024).decode()
		print(connection)
		if connection == "Connection failed\n":
			sys.exit(1)
		cmdline = clientCmd(s)
		handler = threading.Thread(target = getmsg, args = (cmdline,))
		handler.start()
		cmdline.cmdloop()
	