import sender
from protobuf import account_pb2, login_pb2


def listen(user):
    while True:
        header = user.sock.recv(4)
        length = int.from_bytes(header, byteorder="big", signed=True) - 4
        data = user.sock.recv(length)
        msgId = int.from_bytes(data[:4], byteorder="big", signed=True)
        body = data[4:]
        if msgId == 102:
            reply = account_pb2.SCLoginResult()
            reply.ParseFromString(body)
            user.sock.close()
            user.address = reply.gameAddress.split(":")
            user.sessionId = reply.sessionId
            user.serverId = reply.serverId
            break
        elif (msgId == 104):
            reply = account_pb2.SCLoginGateResult()
            reply.ParseFromString(body)
            sender.queue(user)
        elif (msgId == 1002):
            reply = login_pb2.SCQueryCharactersResult()
            reply.ParseFromString(body)
            sender.create(user, "python")
        elif (msgId == 1004):
            reply = login_pb2.SCCharacterCreateResult()
            reply.ParseFromString(body)
            user.humanId = reply.humanId
            sender.gateLogin(user, user.humanId)
