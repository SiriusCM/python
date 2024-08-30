from protobuf import account_pb2, login_pb2, test_pb2, friend_pb2


def createCSGmCmd(command):
    csGmCmd = test_pb2.CSGmCmd()
    csGmCmd.command = command
    return csGmCmd


def createCSLogin(account):
    cslogin = account_pb2.CSLogin()
    cslogin.account = account
    cslogin.password = ""
    cslogin.version = "1.2.0"
    cslogin.phoneInfo.CopyFrom(createDPhone())
    cslogin.sdkType = 0
    cslogin.serverUUID = 20002
    return cslogin


def createCSLoginGate(account, sessionId, serverUUID):
    cslogingate = account_pb2.CSLoginGate()
    cslogingate.account = account
    cslogingate.sessionId = sessionId
    cslogingate.phoneInfo.deviceId = "a78d3975ec55f49e71cc4c2bb64e2030cb60a503"
    cslogingate.phoneInfo.deviceModel = "System Product Name (ASUS)"
    cslogingate.phoneInfo.deviceSys = "Windows 10  (10.0.19042) 64bit"
    cslogingate.phoneInfo.deviceRam = "16294"
    cslogingate.phoneInfo.mac = ""
    cslogingate.phoneInfo.idfa = ""
    cslogingate.phoneInfo.os = 4
    cslogingate.phoneInfo.language = "CN"
    cslogingate.sdkType = 0
    cslogingate.serverUUID = serverUUID
    return cslogingate


def createDPhone():
    dphone = account_pb2.DPhone()
    dphone.deviceId = "a78d3975ec55f49e71cc4c2bb64e2030cb60a503"
    dphone.deviceModel = "System Product Name (ASUS)"
    dphone.deviceSys = "Windows 10  (10.0.19042) 64bit"
    dphone.deviceRam = "16294"
    dphone.mac = ""
    dphone.idfa = ""
    dphone.os = 4
    dphone.language = "CN"
    return dphone


def createCSQueryCharacters():
    csQueryCharacters = login_pb2.CSQueryCharacters()
    return csQueryCharacters


def createCSCharacterCreate(name):
    csCharacterCreate = login_pb2.CSCharacterCreate()
    csCharacterCreate.name = name
    return csCharacterCreate


def createCSCharacterLogin(humanId):
    csCharacterLogin = login_pb2.CSCharacterLogin()
    csCharacterLogin.humanId = humanId
    return csCharacterLogin


def createCSRequestFriend(beReqId):
    csRequestFriend = friend_pb2.CSRequestFriend()
    csRequestFriend.beReqId.append(beReqId)
    return csRequestFriend
