import asyncio
import importlib
from threading import Thread

import login
import scene
import transport
import web


async def main():
    importlib.reload(login)
    thread = Thread(target=web.create_server, args=('0.0.0.0', 8888))
    thread.start()
    thread = Thread(target=scene.start, args=())
    thread.start()

    server = await asyncio.get_running_loop().create_server(transport.Transport, '0.0.0.0', 9999)
    await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
