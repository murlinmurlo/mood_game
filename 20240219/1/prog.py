import os
import sys
import glob
import zlib

def main():
    if len(sys.argv) == 1:
        raise Exception("Not a repository")
    
    elif len(sys.argv) == 2:
        path = sys.argv[1]
        branches = glob.iglob(path + '/.git/refs/heads/*')
        for b in branches:
            print(os.path.basename(b))

    file = glob.iglob(os.path.join(".git/refs/heads", sys.argv[1])).__next__()
    with open(file, "r") as f:
        f_hash = f.read().split()[0]

    while len(list(glob.iglob(os.path.join(".git/objects", f_hash[0:2], f_hash[2:])))) > 0:
        parent, parent_tree = print_last_commit_tree(f_hash)
        print_last_history()


def print_last_commit_tree(commit):
    file = os.path.join(".git/objects", commit[0:2], commit[2:])
    with open(file, "rb") as f:
        data = zlib.decompress(f.read())
    
    lines = data.split(b"\n")
    tree_line = next(line for line in lines if line.startswith(b"tree"))
    parent_line = next(line for line in lines if line.startswith(b"parent"))
    
    tree = tree_line.decode().split("tree")[1].strip()
    parent_tree = parent_line.decode().split("parent")[1].strip()
    
    print(f"TREE for commit {commit}")
    return parent_tree, tree


def print_last_history():
    pass


if __name__ == "__main__":
    main()
