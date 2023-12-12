import socket
import threading

import receiver


class User:
    account = None
    address = None
    sessionId = None
    serverId = None
    humanId = None
    sock = None
    key = None
    _i = 0
    _j = 0

    def __init__(self, account):
        self.account = account

    async def connect(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, port))
        self.setKey()
        # t = threading.Thread(target=receiver.listen, args=(self,))
        # t.start()
        receiver.listen(self)

    def setKey(self):
        length = int.from_bytes(self.sock.recv(4), byteorder="big", signed=True) - 4
        self.key = self.sock.recv(length)
        T = bytearray().zfill(256)
        S = bytearray().zfill(256)
        for jj in range(0, 256):
            S[jj] = jj
            T[jj] = self.key[jj % length]
        j = 0
        for jj in range(0, 256):
            j = ((j + S[jj] + T[jj]) % 256) & 0xFF
            t = S[jj]
            S[jj] = S[j]
            S[j] = t
        self.key = S
        self._i = 0
        self._j = 0
        self.working = True

    def build(self, msgId, body):
        builder = bytearray() + msgId.to_bytes(4, "big") + body.SerializeToString()
        for i in range(0, len(builder)):
            self._i = ((self._i + 1) % 256) & 0xFF
            self._j = ((self._j + self.key[self._i]) % 256) & 0xFF
            temp = self.key[self._i]
            self.key[self._i] = self.key[self._j]
            self.key[self._j] = temp
            t = ((self.key[self._i] + self.key[self._j]) % 256) & 0xFF
            k = self.key[t]
            builder[i] = k ^ builder[i]
        builder = (len(builder) + 4).to_bytes(4, "big") + builder
        return builder
