import pandas

import data
import event
import msg.person_pb2 as person_pb2
from account import Account, route

confCoops = pandas.read_excel('conf/Coop.xlsx', sheet_name='协力者|Coop', header=2, index_col=0)


@route(1101)
def login(account: Account, message):
    confCoop = confCoops.loc[12]
    name = confCoop['name']
    rets = data.execute('select * from game_human_open_world_coop_0 limit 1')
    person = person_pb2.Person()
    person.ParseFromString(message)
    event.fire(account, '登录')
    print('login')


@route(1102)
def logout(account: Account, message):
    event.fire(account, '离线')
    print('logout')
