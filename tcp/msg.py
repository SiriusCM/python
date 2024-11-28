msgIdDict = {}


def route(msgid):
    def handler(fn):
        msgIdDict[msgid] = fn
        return fn

    return handler


def dispatch(transport, msgid, message):
    fun = msgIdDict[msgid]
    fun(transport, message)
