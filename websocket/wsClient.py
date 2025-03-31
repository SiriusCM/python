import asyncio
import json

import websockets


async def task(name: str, msg: str):
    uri = "ws://localhost:8765/ws"
    async with websockets.connect(uri) as websocket:
        login = json.dumps({"type": "login", "username": name, "roomId": "123"})
        await websocket.send(login)
        await websocket.recv()
        message = json.dumps({"type": "message", "message": msg})
        while True:
            await websocket.send(message)
            await websocket.recv()
            await asyncio.sleep(1)


async def main():
    list = []
    for i in range(2):
        t = task('gao' + str(i), str(i))
        list.append(t)
    await asyncio.gather(*list)


asyncio.run(main())
