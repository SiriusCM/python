eventDict = {}


def listen(key):
    def handler(fn):
        if key not in eventDict:
            eventDict[key] = {}
        if fn not in eventDict[key]:
            eventDict[key][fn.__module__ + '.' + fn.__name__] = fn
        return fn

    return handler


def fire(role, key):
    if key not in eventDict:
        return
    for name in eventDict[key]:
        eventDict[key][name](role)
