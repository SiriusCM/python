import asyncio


async def tcp_client():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    message = {'a': '1', 'b': '2', 'c': '3'}
    data = str(message).encode()
    data = (1101).to_bytes(length=4, byteorder='little') + data
    writer.write(data)
    await writer.drain()
    await reader.read(1000)


if __name__ == '__main__':
    asyncio.run(tcp_client())
