import asyncio
import importlib

import account
import cell.login as login


async def main():
    importlib.reload(login)
    server = await asyncio.get_running_loop().create_server(account.Account, '0.0.0.0', 8888)
    await server.serve_forever()


if __name__ == '__main__':
    asyncio.run(main())
