import cmd
import cowsay
import shlex
import sys
import io

FIELD = 10
custom_monster = cowsay.read_dot_cow(io.StringIO("""
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
"""))

class Monster:
    def __init__(self, name, hello, hp):
        self.hello = hello
        self.name = name
        self.hp = int(hp) 

    def say(self):
        if self.name == "jgsbat":
            print(cowsay.cowsay(self.hello, cowfile=custom_monster))
        else:
            print(cowsay.cowsay(self.hello, cow=self.name))

class Field:
    def __init__(self):
        self.matrix = {(x, y): None for x in range(10) for y in range(10)}

    def addmon(self, name, x, y, hello, hp):
        if self.matrix.get((x, y)) is not None:
            print("Replaced the old monster")

        if name in cowsay.list_cows() + ["jgsbat"]:
            self.matrix[(x, y)] = Monster(name, hello, hp)
            print(f"Added monster {name} to ({x}, {y}) saying {hello} hp {int(hp)}")
        else:
            print("Cannot add unknown monster")

class Player:
    def __init__(self):
        self.player_pos = (0, 0)

    def encounter(self, field):
        if field.matrix.get(self.player_pos) is not None:
            field.matrix[self.player_pos].say()

    def move(self, direction, field):
        x, y = self.player_pos
        if direction == "up":
            y = (y - 1) % FIELD 
        elif direction == "down":
            y = (y + 1) % FIELD 
        elif direction == "left":
            x = (x - 1) % FIELD 
        elif direction == "right":
            x = (x + 1) % FIELD 
        self.player_pos = (x, y)
        print(f"Moved to {self.player_pos}")
        self.encounter(field)

<<<<<<< HEAD
    def attack(self, field, weapon="sword"):
=======
    def attack(self, field, monster_name):
>>>>>>> attack_by_name
        if field.matrix.get(self.player_pos) is None:
            print("No monster here")
            return

        monster = field.matrix[self.player_pos]
<<<<<<< HEAD
        if weapon == "sword":
=======
        if monster.name != monster_name:
            print(f"No {monster_name} here")
            return

        if monster.hp >= 10:
>>>>>>> attack_by_name
            damage = 10
        elif weapon == "spear":
            damage = 15
        elif weapon == "axe":
            damage = 20
        else:
            print("Unknown weapon")
            return

        print(f"Attacked {monster.name} with {weapon}, damage {damage} hp")
        
        monster.hp -= damage
        if monster.hp <= 0:
            del field.matrix[self.player_pos]
            print(f"{monster.name} died")
        else:
            print(f"{monster.name} now has {monster.hp} hp")


class GameCmd(cmd.Cmd):
    intro = "<<< Welcome to Python-MUD 0.1 >>>"
    prompt = "> "

    def __init__(self, player, field):
        super().__init__()
        self.player = player
        self.field = field

    def do_up(self, arg):
        """Move the player up"""
        self.player.move("up", self.field)

    def do_down(self, arg):
        """Move the player down"""
        self.player.move("down", self.field)

    def do_left(self, arg):
        """Move the player left"""
        self.player.move("left", self.field)

    def do_right(self, arg):
        """Move the player right"""
        self.player.move("right", self.field)

    def do_addmon(self, arg):
        """Add a monster to the field"""
        args = shlex.split(arg)
        if len(args) == 8 and args[0] in cowsay.list_cows() + ["jgsbat"]:
            x, y, hello, hp = args[2], args[3], args[5], args[7]
            self.field.addmon(args[0], int(x), int(y), hello, hp)
        else:
            print("Invalid command format")

    def do_EOF(self, line):
        """Exit the game"""
        return True

    def emptyline(self):
        """Do nothing on empty input"""
        pass

    def complete_attack(self, text, line, begidx, endidx):
        monster_names = [name for name in cowsay.list_cows() if name != "jgsbat"]
        if not text:
            completions = monster_names
        else:
            completions = [name for name in monster_names if name.startswith(text)]
        return completions

    def do_attack(self, arg):
        """Attack the monster"""
        args = shlex.split(arg)
        if len(args) != 1:
            print("Invalid command format")
            return
        monster_name = args[0]
        if self.field.matrix.get(self.player.player_pos) is None:
            print("No monster here")
            return
        if monster_name not in cowsay.list_cows():
            print(f"No monster with the name {monster_name} here")
            return
        self.player.attack(self.field, monster_name)


player1 = Player()
field1 = Field()
game_cmd = GameCmd(player1, field1)
game_cmd.cmdloop()
