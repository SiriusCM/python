import time
from queue import Queue
from threading import Thread

scenes = []


def start():
    while True:
        for scene in scenes:
            scene.pulse()
        time.sleep(0.1)


class WorldObject:
    def pulse(self):
        pass


class RoleObject(WorldObject):
    def __init__(self, transport):
        self.transport = transport

    def write(self, data):
        self.transport.write(data)


class SceneObject(WorldObject):
    consumer = Queue()
    worldObjects = []

    def create(self):
        thread = Thread(target=self.pulse, args=())
        thread.start()

    def pulse(self):
        while self.consumer.not_empty:
            self.consumer.get()()
        for worldObject in self.worldObjects:
            worldObject.pulse()

    def addConsumer(self, fun):
        self.consumer.put(fun)
