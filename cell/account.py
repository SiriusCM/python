import asyncio


class Account(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        msgid = int.from_bytes(data[0:4], byteorder='little')
        message = data[4:]
        handler = msgIdDict[msgid]
        handler(self, message)

    def connection_lost(self, exc):
        pass

    def write(self, data):
        self.transport.write(data)


msgIdDict = {}


def route(msgid):
    def handler(fn):
        msgIdDict[msgid] = fn
        return fn

    return handler
