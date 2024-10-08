import time
from itertools import groupby

import pymysql
from pymysql import cursors

import sender

pathList = '/game-record/v1/role-list?client_id=5uk4xyrzhotypyeb7e&limit=1'
pathRole = '/game-record/v1/upload-role-profile?client_id=5uk4xyrzhotypyeb7e'
pathBasic = '/game-record/v1/upload-basic-data?client_id=5uk4xyrzhotypyeb7e'
pathCollection = '/game-record/v1/upload-collection-data?client_id=5uk4xyrzhotypyeb7e'


def postTapData(ip, database, minites):
    ret = sender.get(pathList)
    print(ret.content.decode())
    t = str(time.time() * 1000 - minites * 60 * 1000)

    db = pymysql.connect(cursorclass=cursors.DictCursor, host=ip, user='root',
                         password='N2kH5lJVJLAHWObs',
                         database=database)
    tapDataList = select(db,
                         'SELECT ltrim(role_id) AS role_id,role_name,`level`,ltrim(thiefNum) AS `怪盗数量`, ltrim(personaNum) AS `人格面具`, ltrim(achievementNum) AS `成就`,`rank` AS `心之海段位`,ltrim(unionBossScore) AS `公会Boss总分`,questName AS `玩家主线进度` FROM game_tap_human_0 WHERE logoutTime > ' + t)
    condition = '('
    for tapData in tapDataList:
        condition = condition + tapData['role_id'] + ','
    condition = condition[0:-1]
    condition += ')'

    thiefs = select(db,
                    'select id,humanId,ltrim(role_id) as role_id,sn,`name` AS `名称`,ltrim(`level`) AS `等级`,ltrim(awakeLevel) AS `觉醒等级`,ltrim(star) AS `星级` FROM game_tap_thief_0 WHERE role_id in ' + condition)
    thiefListMap = groupby(thiefs, key=lambda x: x['role_id'])
    weapons = select(db,
                     'select id,humanId,ltrim(role_id) as role_id,sn,`name` AS `名称`,ltrim(`level`) AS `等级`,ltrim(remouldCount) AS `改造等级`,ltrim(star) AS `星级` FROM game_tap_weapon_0 WHERE role_id in ' + condition)
    weaponListMap = groupby(weapons, key=lambda x: x['role_id'])
    coops = select(db,
                   'select id,humanId,ltrim(role_id) as role_id,sn,`name` AS `名称`,ltrim(`level`) AS `等级` FROM game_tap_coop_0 WHERE role_id in ' + condition)
    coopListMap = groupby(coops, key=lambda x: x['role_id'])
    db.close()

    data = []
    for tapData in tapDataList:
        data.append({'role_id': tapData['role_id'], 'role_name': tapData['role_name'], 'level': tapData['level']})
    ret = sender.post(pathRole, {'data': data})
    print(ret.content)

    data = []
    for tapData in tapDataList:
        role_data = [{'field': '怪盗数量', 'value': tapData['怪盗数量']},
                     {'field': '人格面具', 'value': tapData['人格面具']},
                     {'field': '成就', 'value': tapData['成就']},
                     {'field': '心之海段位', 'value': tapData['怪盗数量']},
                     {'field': '公会Boss总分', 'value': tapData['公会Boss总分']},
                     {'field': '玩家主线进度', 'value': tapData['玩家主线进度']}]
        data.append({'role_id': tapData['role_id'], 'role_data': role_data})
    ret = sender.post(pathBasic, {'type': 1, 'data': data})
    print(ret.content)

    data = []
    for thiefList in thiefListMap:
        role_data = []
        for thief in thiefList[1]:
            role_data.append({'id': thief['id'], 'sn': thief['sn'],
                              'optional_field': {'field_1': thief['名称'], 'field_2': thief['等级'],
                                                 'field_3': thief['觉醒等级'], 'field_4': thief['星级']}})
        data.append({'role_id': thiefList[0], 'role_data': role_data})
    ret = sender.post(pathCollection, {'type': 1, 'data': data})
    print(ret.content)

    data = []
    for weaponList in weaponListMap:
        role_data = []
        for weapon in weaponList[1]:
            role_data.append({'id': weapon['id'], 'sn': weapon['sn'],
                              'optional_field': {'field_1': weapon['名称'], 'field_2': weapon['等级'],
                                                 'field_3': weapon['星级'], 'field_4': weapon['改造等级']}})
        data.append({'role_id': weaponList[0], 'role_data': role_data})
    ret = sender.post(pathCollection, {'type': 2, 'data': data})
    print(ret.content)

    data = []
    for coopList in coopListMap:
        role_data = []
        for coop in coopList[1]:
            role_data.append({'id': coop['id'], 'sn': coop['sn'],
                              'optional_field': {'field_1': coop['名称'], 'field_2': coop['等级']}})
        data.append({'role_id': coopList[0], 'role_data': role_data})
    ret = sender.post(pathCollection, {'type': 3, 'data': data})
    print(ret.content)


def select(db, sql):
    cursor = db.cursor()
    cursor.execute(sql)
    rets = cursor.fetchall()
    return rets


if __name__ == '__main__':
    ip = '10.77.38.188'
    database = 'persona5_15_tap_'
    postTapData(ip, database + '0', 90)
    postTapData(ip, database + '1', 90)
