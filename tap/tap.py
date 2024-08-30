import time
from concurrent.futures import ThreadPoolExecutor

import pymysql
from pymysql import cursors

import mysql
import sender

ips = ['10.148.154.122', '10.148.154.92', '10.148.154.47', '10.148.154.105', '10.148.154.54', '10.148.154.65',
       '10.148.154.127', '10.148.154.34', '10.148.154.52',
       '10.148.154.21', '10.148.154.111', '10.148.154.41', '10.148.154.117', '10.148.154.43', '10.148.154.19',
       '10.148.154.36', '10.148.154.33',
       '10.148.154.35', '10.148.154.38', '10.148.154.18', '10.148.154.31', '10.148.154.23', '10.148.154.45',
       '10.148.154.42', '10.148.154.48']

ips = ['10.77.38.188']

pathList = '/game-record/v1/role-list?client_id=5uk4xyrzhotypyeb7e&limit=1'
pathRole = '/game-record/v1/upload-role-profile?client_id=5uk4xyrzhotypyeb7e'
pathBasic = '/game-record/v1/upload-basic-data?client_id=5uk4xyrzhotypyeb7e'
pathCollection = '/game-record/v1/upload-collection-data?client_id=5uk4xyrzhotypyeb7e'

minute = 90
accounts = {}
humanIdList = {}


def main():
    ret = sender.get(pathList)
    print(ret.content.decode())

    timestamp = round(time.time())

    i = 0
    for ip in ips:
        for j in range(0, 2):
            index = i + j
            db = pymysql.connect(cursorclass=cursors.DictCursor, host=str(ip), user='root', password='N2kH5lJVJLAHWObs',
                                 database='persona5_15_game_' + str(index))
            humanIds = mysql.select(db, 'select id from game_human_online_time_0 where loginTime > ' + str(
                timestamp * 1000 - minute * 60 * 1000))
            humanIdList[index] = humanIds
            db.close()
        i = i + 2
    i = 0
    for ip in ips:
        for j in range(0, 2):
            index = i + j
            db = pymysql.connect(cursorclass=cursors.DictCursor, host=str(ip), user='root', password='N2kH5lJVJLAHWObs',
                                 database='persona5_15_game_' + str(index))
            condition = '('
            for humanIds in humanIdList:
                for humanId in humanIdList[humanIds]:
                    condition += str(humanId['id'])
                    condition += ','
            condition = condition[0:- 1]
            condition += ')'
            accountMap = mysql.select(db, 'select id,userId from game_human_account_0 where id in ' + condition)
            db.close()
            for account in accountMap:
                accounts[account['id']] = str(account['userId'])
        i = i + 2
    i = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        for ip in ips:
            for j in range(0, 2):
                index = i + j
                executor.submit(task, ip, index)
            i = i + 2


def task(ip, index):
    if len(humanIdList[index]):
        return
    db = pymysql.connect(cursorclass=cursors.DictCursor, host=str(ip), user='root', password='N2kH5lJVJLAHWObs',
                         database='persona5_15_game_' + str(index))
    condition = '('
    for humanId in humanIdList[index]:
        condition += str(humanId['id'])
        condition += ','
    condition = condition[0:- 1]
    condition += ')'

    body = mysql.select_role(db, condition, accounts)
    ret = sender.post(pathRole, body)
    print(ret.content.decode())

    body = mysql.select_base(db, condition, accounts)
    ret = sender.post(pathBasic, body)
    print(ret.content.decode())

    body = mysql.select_thief(db, condition, accounts)
    ret = sender.post(pathCollection, body)
    print(ret.content.decode())

    body = mysql.select_weapon(db, condition, accounts)
    ret = sender.post(pathCollection, body)
    print(ret.content.decode())

    body = mysql.select_coop(db, condition, accounts)
    ret = sender.post(pathCollection, body)
    print(ret.content.decode())

    db.close()


if __name__ == '__main__':
    main()
