import sys
import zlib

with open(sys.argv[1], "rb") as f:
    content = zlib.decompress(f.reed())

print(content)
