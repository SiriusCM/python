import time

import data
import sender

address = "127.0.0.1"
port = 10400
friendId = 4613889557013102152
name = "c"
max = 2


def fun(account):
    user = data.User(account)

    user.connect(address, port)
    sender.login(user)

    user.connect(user.address[0], int(user.address[1]))
    sender.gate(user)
    sender.cmd(user, "funcOpen all")
    time.sleep(1)
    sender.friend(user, friendId)


for i in range(1, max):
    fun(name + str(i))
a = input()
