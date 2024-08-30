import msg


def cmd(user, command):
    req = user.build(9937, msg.createCSGmCmd(command))
    user.sock.sendall(req)


def login(user):
    req = user.build(101, msg.createCSLogin(user.account))
    user.sock.sendall(req)


def gate(user):
    req = user.build(103, msg.createCSLoginGate(user.account, user.sessionId, user.serverId))
    user.sock.sendall(req)


def queue(user):
    req = user.build(1001, msg.createCSQueryCharacters())
    user.sock.sendall(req)


def create(user, name):
    req = user.build(1003, msg.createCSCharacterCreate(name))
    user.sock.sendall(req)


def gateLogin(user, humanId):
    req = user.build(1007, msg.createCSCharacterLogin(humanId))
    user.sock.sendall(req)


def friend(user, beReqId):
    req = user.build(1911, msg.createCSRequestFriend(beReqId))
    user.sock.sendall(req)
