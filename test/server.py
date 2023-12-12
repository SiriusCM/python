import asyncio
import socket


async def accept(s):
    client, addr = s.accept()
    print(addr)
    while True:
        head = client.recv(4)
        if head == b'':
            client.close()
            return
        data = client.recv(int.from_bytes(head, byteorder='big') - 4)
        print(str(data, 'utf-8'))


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 2525))
server.listen(100)
while True:
    asyncio.run(accept(server))
