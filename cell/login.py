import pandas

import account as account
import data as data
import msg.person_pb2 as person_pb2
from account import Account

confCoops = pandas.read_excel('conf/Coop.xlsx', sheet_name='协力者|Coop', header=2, index_col=0)


@account.route(1101)
def login(account: Account, message):
    confCoop = confCoops.loc[12]
    name = confCoop['name']
    rets = data.execute('select * from game_human_open_world_coop_0 limit 1')
    person = person_pb2.Person()
    person.ParseFromString(message)
    print('login')


@account.route(1102)
def logout(account: Account, message):
    print('logout')
