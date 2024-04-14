import cowsay
import shlex
import io
import sys
import cmd
import asyncio
import random

DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Вправо, влево, вверх, вниз
DIRECTION_NAMES = ["right", "left", "up", "down"]

clients = {}


monsters = {}

class Player():
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
		
	def moving(self, dx, dy):
		self.x = (self.x + dx) % 10
		self.y = (self.y + dy) % 10
		responce = (f"Moved to ({self.x}, {self.y})")
		if (self.x*10 + self.y) in monsters:
			responce += encounter(self.x, self.y)
		return responce
		
	def attack(self,name, weapon = "sword"):
		if (self.x*10 + self.y) not in monsters:
			return "No monster here"
		mon = monsters[self.x*10 + self.y]
		if weapon == "sword":
			dmg = 10
		elif weapon == "spear":
			dmg = 15
		elif weapon == "axe":
			dmg = 20

		responce = (f"Attacked {mon[0]} with {weapon}, damage {dmg} hp")
		mon[2]-=dmg
		if mon[2] <= 0:
			responce += (f"\n{mon[0]} died")
			del monsters[self.x*10 + self.y]
		else:
			responce += (f"\n{mon[0]} now has {mon[2]}")
		return responce
		

jgsbat = cowsay.read_dot_cow(io.StringIO('''
$the_cow = <<EOC;
         $thoughts
          $thoughts
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\--//|.'-._  (
     )'   .'\/o\/o\/'.   `(
      ) .' . \====/ . '. (
       )  / <<    >> \  (
        '-._/``  ``\_.-'
  jgs     __\\'--'//__
         (((""`  `"")))
EOC
'''))

def encounter(x,y):
    if monsters[x*10+y][0] == "jgsbat":
        return (cowsay.cowsay(monsters[x*10+y][1], cowfile = jgsbat))
    else:
        return(cowsay.cowsay(monsters[x*10+y][1], cow = monsters[x*10+y][0]))

def addmon(name, x, y, hello, hitpoints):
    if name not in cowsay.list_cows() and name != "jgsbat":
        print("Cannot add unknown monster")
        return
    oldmon = False
    if (x*10+y) in monsters:
        oldmon = True
    monsters[x*10+y] =[name, hello, hitpoints]
    responce = (f"Added monster {name} with {hitpoints} hp")
    if oldmon:
        responce += ("\nReplaced the old monster")
    return responce

async def sayall(username, message):
    for out in clients.values():
        await out.put(f"{username}: {message}")
        

async def chat(reader, writer):
    username = await reader.readline()
    username = username.decode()
    username = username[:len(username)-1]
    if username in clients:
        writer.write("Connection failed\n".encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return
    print("Connected with", username)
    for out in clients.values():
        await out.put(f"{username} joined the server\n")
    writer.write(f"{username} joined the server\n".encode()) 
    await writer.drain()
    clients[username] = asyncio.Queue()
    player = Player()
    send = asyncio.create_task(reader.readline())
    receive = asyncio.create_task(clients[username].get())
    while not reader.at_eof():
        done, pending = await asyncio.wait([send, receive], return_when=asyncio.FIRST_COMPLETED)
        for q in done:
            if q is send:
                send = asyncio.create_task(reader.readline())
                if len(q.result()) != 0:
                    com, *args = shlex.split(q.result().decode())
                    match com:
                        case "move":
                            await clients[username].put(player.moving(int(args[0]), int(args[1])))
                        case "addmon":
                            res = addmon(args[0], int(args[1]), int(args[2]), args[3], int(args[4]))
                            for out in clients.values():
                                await out.put(username+ " " + res)
                        case "attack":
                            if len(args) == 1:
                                res = player.attack(args[0])
                                if res == "No monster here":
                                    await clients[username].put(res)
                                else:
                                    for out in clients.values():
                                        await out.put(username+ " " + res)
                            else:
                                res = player.attack(args[0], args[2])
                                if res == "No monster here":
                                    await clients[username].put(res)
                                else:
                                    for out in clients.values():
                                        await out.put(username + " " +res)
                        case "sayall":
                            await sayall(username, ' '.join(args))
            elif q is receive:
                receive = asyncio.create_task(clients[username].get())
                writer.write(f"{q.result()}\n".encode())
                await writer.drain()
    send.cancel()
    receive.cancel()
    print(username, "DONE")
    del clients[username]
    for out in clients.values():
        await out.put(f"{username} left the server\n")
    writer.close()
    await writer.wait_closed()


    async def move_monsters():
    while True:
        if monsters:
            monster_location, monster_info = random.choice(list(monsters.items()))
            x, y = divmod(monster_location, 10)
            while True:
                dx, dy = random.choice(DIRECTIONS)
                new_x, new_y = (x + dx) % 10, (y + dy) % 10
                if new_x * 10 + new_y not in monsters:  # Если клетка свободна
                    del monsters[monster_location]
                    monsters[new_x * 10 + new_y] = monster_info
                    direction = DIRECTION_NAMES[DIRECTIONS.index((dx, dy))]
                    message = f"{monster_info[0]} moved one cell {direction}"
                    for out in clients.values():
                        await out.put(message)
                    break
        await asyncio.sleep(30)  # Пауза 30 секунд

	
async def main():
    server = await asyncio.start_server(chat, '0.0.0.0', 1337)
    async with server:
        asyncio.create_task(move_monsters())
        await server.serve_forever()

asyncio.run(main())
