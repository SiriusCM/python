import asyncio

from websockets.asyncio.server import serve


async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)


async def main():
    async with serve(echo, "localhost", 8765) as ws:
        await ws.serve_forever()


asyncio.run(main())
