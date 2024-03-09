import cowsay
import sys
import shlex

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0

    def encounter(self, x, y):
        print(cowsay.cow("Hello!"))

    def move(self, direction):
        if direction == "up":
            self.y = (self.y - 1) % 10
        elif direction == "down":
            self.y = (self.y + 1) % 10
        elif direction == "left":
            self.x = (self.x - 1) % 10
        elif direction == "right":
            self.x = (self.x + 1) % 10


class Monster:
    def __init__(self, x, y, hello, hp):
        self.x = x
        self.y = y
        self.hello = hello
        self.hp = hp

    def encounter(self):
        print(cowsay.cow(self.hello))

class Game:
    def __init__(self):
        self.player = Player()
        self.monsters = []

    def addmon(self, monster_name, hello_string, hp, x, y):
        try:
            hp = int(hp)
        except ValueError:
            print("Invalid value for hp. Expecting an integer.")
            return

        for monster in self.monsters:
            if monster.x == x and monster.y == y:
                monster.hello = hello_string
                monster.hp = hp
                if monster_name not in cowsay.list_cows:
                    print("Cannot add unknown monster")
                    return
                print("Monster replaced.")
                return
        
        self.monsters.append(Monster(x, y, hello_string, hp))
        print(f"Added monster at position ({x}, {y}) with greeting: {hello_string}")

    def run(self):
        while True:
            command = shlex.split(input().strip())
            if len(command) == 0:
                continue
            elif command[0] == "up":
                self.player.move("up")
            elif command[0] == "down":
                self.player.move("down")
            elif command[0] == "left":
                self.player.move("left")
            elif command[0] == "right":
                self.player.move("right")
            elif command[0] == "addmon":
                if len(command) != 9:
                    print("Invalid arguments")
                    continue
                monster_name = command[1]
                hello_string = command[3]
                hp = command[5]
                x = int(command[7])
                y = int(command[8])
                self.addmon(monster_name, hello_string, hp, x, y)
            else:
                print("Invalid command")

            print(f"Moved to position ({self.player.x}, {self.player.y})")

            for monster in self.monsters:
                if monster.x == self.player.x and monster.y == self.player.y:
                    self.player.encounter(monster.x, monster.y)
                    break

game = Game()
game.run()
