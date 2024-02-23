
import zlib
import glob
import sys

for store in glob.iglob(sys.argv[1] + "/??/"):

    with open(store, "rb") as f:
        obj = zlib.decompress(f.read())
        print("\t########\n", content)

b = b"qwe\qweqwe\qweqweqwe"
s = b.decode()
print(s)
