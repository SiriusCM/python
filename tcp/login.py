import msg
from account import Account


@msg.route(1101)
def login(transport: Account, message):
    print('login')
    transport.password = message


@msg.route(1102)
def logout(transport: Account, message):
    print('logout')
