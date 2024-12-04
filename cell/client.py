import asyncio

import msg.person_pb2


async def tcp_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    person = msg.person_pb2.Person()
    person.id = 5
    person.name = 'asdsad'
    message = (1101).to_bytes(length=4, byteorder='little') + person.SerializeToString()

    writer.write(message)
    await writer.drain()
    await reader.read(1000)


if __name__ == '__main__':
    asyncio.run(tcp_client())
