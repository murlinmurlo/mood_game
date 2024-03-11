import cmd

class Echoer(cmd.Cmd):
    """Echo console"""
    prompt = "~ "
    words = "one", "two", "three","four", "five"

    def complete_echo(self, text, line, begidx, endeidx):
        return [c for c in self.words if c.startwith(text)]
    
    def do_echo(self, args):
        """echo any string"""
        print(args)

    def do_EOE(self, args):
        return True
    
    def emptyline(self):
        pass


if __name__ == "__main__":
    Echoer.cmdloop()
