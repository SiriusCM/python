import asyncio

from cell.scene import RoleObject, SceneObject


class Transport(asyncio.Protocol):
    def connection_made(self, transport):
        self.role = RoleObject(transport)
        self.role.scene = SceneObject()
        self.role.scene.create()

    def data_received(self, data):
        msgid = int.from_bytes(data[0:4], byteorder='little')
        message = data[4:]
        handler = msgIdDict[msgid]
        self.role.scene.addConsumer(lambda: handler(self.role, message))

    def connection_lost(self, exc):
        pass


msgIdDict = {}


def route(msg_id):
    def handler(fn):
        msgIdDict[msg_id] = fn
        return fn

    return handler
