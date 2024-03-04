import shlex
import sys


fio = sys.argv[1]
b_place = sys.argv[2]

print(shlex.join(["register", fio, b_place]))
