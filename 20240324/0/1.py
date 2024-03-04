import shlex
while True:
	s = input()
	res  = shlex.split(s)
	print(res)
