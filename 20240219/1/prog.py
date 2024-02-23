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


if __name__ == "__main__":
    main()
