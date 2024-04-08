import sys
import cmd

class Sayer(cmd.Cmd):
    def do_bless(self, args):
        printf(f"Be blessed {args}!")

    def do_sendto(self, args):
        printf(f"Go to {args}")

    def do_bless(self, args):
        return True
if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as file:
            saycmd = Sayer(stdin = file)
            saycmd.prompt = ""
            saycmd.use_rawinput     = False
    else:
        saycmd = Sayer()
    Sayer().cmdloop()
