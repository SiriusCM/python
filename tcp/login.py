import pandas

import data
import msg
from account import Account

confCoops = pandas.read_excel('conf/Coop.xlsx', sheet_name=0, header=2, index_col=0)


@msg.route(1101)
def login(transport: Account, message):
    print('login')
    rets = data.execute('select * from game_human_open_world_coop_0 limit 1')
    confCoop = confCoops.loc[12]
    name = confCoop['name']
    transport.password = message


@msg.route(1102)
def logout(transport: Account, message):
    print('logout')
