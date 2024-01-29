import asyncio
import socket

ip = '10.4.4.208'
port = 10000
loop = asyncio.get_event_loop()
list = []


async def job0():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    list.append(sock)


async def job1(sock, msgId):
    data = int(msgId).to_bytes(4, "big") + b'123'
    data = bytearray() + len(data).to_bytes(4, "big") + data
    sock.sendall(data)


async def job2(sock, msgId):
    while True:
        await asyncio.sleep(1)
        data = int(msgId).to_bytes(4, "big") + b'789'
        data = bytearray() + len(data).to_bytes(4, "big") + data
        sock.sendall(data)


async def main0(num):
    tasks1 = []
    for i in range(0, num):
        tasks1.append(loop.create_task(job0()))
    await asyncio.wait(tasks1)


async def main1(msgId):
    tasks2 = []
    for s in list:
        tasks2.append(loop.create_task(job1(s, msgId)))
    await asyncio.wait(tasks2)


async def main2(msgId):
    tasks2 = []
    for s in list:
        tasks2.append(loop.create_task(job2(s, msgId)))
    await asyncio.wait(tasks2)


loop.run_until_complete(main0(1))
input()
loop.run_until_complete(main1(1101))
input()
loop.run_until_complete(main1(1103))
input()
loop.run_until_complete(main2(1105))
input()
