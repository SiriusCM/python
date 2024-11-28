import data
import msg
from account import Account


@msg.route(1101)
def login(transport: Account, message):
    print('login')
    rets = data.execute('select * from game_human_account_0 limit 1')
    transport.password = message


@msg.route(1102)
def logout(transport: Account, message):
    print('logout')
