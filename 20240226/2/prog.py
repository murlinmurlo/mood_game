from cowsay import cowsay, list_cows
import sys
import random

class Player:
    def __init__(self):
        self.x = 0
        self.y = 0

    def encounter(self):
        print(cowsay.cow("Hi!"))

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
    def __init__(self, x, y, name, greeting):
        self.x = x
        self.y = y
        self.name = name
        self.greeting = greeting

    def encounter(self):
        print(cowsay.cow(self.greeting, cow=self.name))


class Game:
    def __init__(self):
        self.player = Player()
        self.monsters = []

    def addmon(self, x, y, name, greeting):
        if name not in cowsay.list_cows():
            print("Cannot add unknown monster")
            return

        for monster in self.monsters:
            if monster.x == x and monster.y == y:
                monster.name = name
                monster.greeting = greeting
                print(f"Monster replaced")
                return

        self.monsters.append(Monster(x, y, name, greeting))
        print(f"Added monster {name} to ({x}, {y}) saying {greeting}")

    def run(self):
        while True:
            command = input().strip().split()
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
                if len(command) != 4:
                    print("Invalid arguments")
                    continue
                x = int(command[1])
                y = int(command[2])
                name = command[3]
                greeting = random.choice(["Hello!", "Don't eat me!!!", "Nice to meet you, white friend!"])
                self.addmon(x, y, name, greeting)
            else:
                print("Invalid command")

            print(f"Moved to ({self.player.x}, {self.player.y})")

            for monster in self.monsters:
                if monster.x == self.player.x and monster.y == self.player.y:
                    monster.encounter()
                    break


game = Game()
game.run()
