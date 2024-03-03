import sys
from cowsay import read_dot_cow, cowthink


cow = read_dot_cow()
message = "".strip()
print(cowthink(sys.argv[1], sys.argv[2], cowfile=cow)
