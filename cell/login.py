import pandas

import data
import event
import msg.person_pb2 as person_pb2
from cell.scene import RoleObject
from transport import route

# confCoops = pandas.read_excel('conf/Coop.xlsx', sheet_name='协力者|Coop', header=2, index_col=0)
confCoops = pandas.read_excel('http://127.0.0.1/Coop.xlsx', sheet_name='协力者|Coop', header=2, index_col=0)


@route(1101)
def login(role: RoleObject, message):
    confCoop = confCoops.loc[12]
    name = confCoop['name']
    role.coop = data.execute('select * from game_human_open_world_coop_0 limit 1')

    person = person_pb2.Person()
    person.ParseFromString(message)

    person = person_pb2.Person()
    person.id = 5
    person.name = 'asdsad'
    message = (1101).to_bytes(length=4, byteorder='little') + person.SerializeToString()
    role.write(message)

    event.fire(role, '登录')
    # print('login')


@route(1102)
def logout(role: RoleObject, message):
    confCoop = confCoops.loc[12]
    name = confCoop['name']

    # print(account.coop)

    person = person_pb2.Person()
    person.ParseFromString(message)

    person = person_pb2.Person()
    person.id = 5
    person.name = 'asdsad'
    message = (1101).to_bytes(length=4, byteorder='little') + person.SerializeToString()
    role.write(message)

    event.fire(role, '离线')
    # print('logout')
