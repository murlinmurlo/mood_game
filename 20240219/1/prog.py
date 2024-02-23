import os
import sys
import glob
import zlib

def main():
    if len(argv) == 1:
        raise Exception("Not a repository")
    
    elif len(argv) == 2:
        path = sys.argv[1]
        branches = glob.iglob(path + '/.git/refs/heads/*')
        for b in branches:
            print(os.path.basename(b))

    file = glob.iglob(os.path.join(".git/refs/heads", sys.argv[1])).__next__()
    with open(file, "r") as f:
        f_hash = f.read().split()[0]

    while len(list(glob.iglob(os.path.join(".git/objects", f_hash[0:2], f_hash[2:])))):
        print_last_commit()
        print_last_commit_tree()
        print_last_history()
    

def print_last_commit():
    pass

def print_last_commit_tree():
    pass

def print_commit_history():
    pass



if __name__ == "__main__":
    main()


