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
        parent_tree, tree = print_last_commit_tree(f_hash)
        print_tree(tree)


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


def print_tree(tree):
    file = os.path.join(".git/objects", tree[0:2], tree[2:])
    with open(tree_file, "rb") as f:
        data = zlib.decompress(f.read())
    header, _, body = data.partition(b'\x00')
    while body:
        treeobj, _, tail = body.partition(b"\x00")
        num, body = tail[:20], tail[20:]
        mode, name = treeobj.split()
        num, body = tail[:20], tail[20:]
        obj_type = "tree"
        if not list(glob.iglob(os.path.join(".git/objects", num.hex()[0:2], num.hex()[2:]))):
            obj_type = "blob"
        print(f"{obj_type} {num.hex()}\t{name.decode()}")


if __name__ == "__main__":
    main()
