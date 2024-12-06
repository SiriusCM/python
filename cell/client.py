import asyncio
import time
from multiprocessing import Process

import msg.person_pb2


async def client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 9999)

    person = msg.person_pb2.Person()
    person.id = 5
    person.name = 'asdsad'

    # message = (1101).to_bytes(length=4, byteorder='little') + person.SerializeToString()
    # writer.write(message)
    # await writer.drain()
    # await reader.read(1000)

    while True:
        message = (1102).to_bytes(length=4, byteorder='little') + person.SerializeToString()
        writer.write(message)
        await writer.drain()
        await reader.read(1000)
        time.sleep(1)


async def mul_client():
    tasks = []
    for i in range(1, 100):
        tasks.append(asyncio.ensure_future(client()))
    await asyncio.gather(*tasks)


def main():
    asyncio.run(mul_client())


if __name__ == '__main__':
    list = []
    for i in range(0, 10):
        process = Process(target=main, args=())
        process.start()
        list.append(process)
    for p in list:
        p.join()
