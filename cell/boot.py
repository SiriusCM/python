import asyncio
import importlib
from threading import Thread

import account
import login
import web


async def main():
    importlib.reload(login)
    thread = Thread(target=web.create_server, args=('0.0.0.0', 8888))
    thread.start()
    server = await asyncio.get_running_loop().create_server(account.Account, '0.0.0.0', 9999)
    await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
