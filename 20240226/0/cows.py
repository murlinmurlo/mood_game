import cowsay
import sys

cows = cowsay.cowsay(sys.argv[1], sys.argv[2])
print(cows)
