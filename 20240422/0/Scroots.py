import unittest
'''
def sqroots(coeffs: str) -> str:
    a, b, c = map(int, coeffs.strip().split(' '))
    if a == 0:
        raise ValueError("a = 0")
        
    d = b**2 - 4*a*c

    if d > 0:
        return f"{(-b + d**(0.5))/(2*a)}, {(-b - d**(0.5))/(2*a)}"
    elif d == 0:
        return f"{-b/(2*a)}"
    else:
        raise ValueError("No real roots")

i = input("")
print(sqroots(i))
'''


'''
import asyncio

async def echo(reader, writer):
    while data := await reader.readline():
        writer.write(data.swapcase())
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
'''
def _serve(port):
    servwr = await asyncio.start_server(_netscroots, "0.0.0.0", port)
    async with server:
        await server.serve_forever()

def server(port):
    asyncio.run(_serve(port))

def scrootnet(coeffs:str, s: socket.socket) -> str:
    s.sendall(coeffs + "\n").encode()
    return s.recv(128).decode().strip()

def client(port):

    params = input(">") 
    with socket.sokcet(socket.AF_INET, socket.SOCK_STREAM) as s:
        s = connect(("localhost", port))
        res = scrootnet(coeffs, s)

    print(res)
