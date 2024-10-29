import time
from itertools import groupby

import pymysql
from pymysql import cursors

import sender

pathList = '/game-record/v1/role-list?client_id=a74m3jogxou10jrcpf&limit=1000'
pathRole = '/game-record/v1/upload-role-profile?client_id=a74m3jogxou10jrcpf'
pathBasic = '/game-record/v1/upload-basic-data?client_id=a74m3jogxou10jrcpf'
pathCollection = '/game-record/v1/upload-collection-data?client_id=a74m3jogxou10jrcpf'
pathCollectionFilter = '/game-record/v1/upload-collection-filter-total?client_id=a74m3jogxou10jrcpf'


def postTapData(ip, database, minites):
    ret = sender.get(pathList)
    role_id_list = eval(ret.text.replace('true', 'True'))['data']['list']
    condition = '('
    for role_id in role_id_list:
        condition = condition + role_id + ','
    if len(condition) <= 1:
        return
    condition = condition[0:-1]
    condition += ')'

    db = pymysql.connect(cursorclass=cursors.DictCursor, host=ip, user='root',
                         password='Nsywl!@#$%^&123',
                         database=database)
    t = str(time.time() * 1000 - minites * 60 * 1000)
    tapDataList = select(db,
                         'SELECT ltrim(role_id) AS role_id,role_name,`level`,awakeLevel,ltrim(portrait) AS avatar_id,portraitFrame AS `头像框`,ltrim(thiefNum) AS `怪盗数量`, ltrim(personaNum) AS `人格面具`, ltrim(achievementNum) AS `成就`,`rank` AS `心之海段位`,ltrim(unionBossScore) AS `公会Boss总分`,questName AS `玩家主线进度` FROM game_tap_human_0 WHERE logoutTime > ' + t + ' AND role_id in ' + condition)
    condition = '('
    for tapData in tapDataList:
        if tapData['role_id'] not in role_id_list:
            continue
        condition = condition + tapData['role_id'] + ','
    if len(condition) <= 1:
        return
    condition = condition[0:-1]
    condition += ')'

    thiefs = select(db,
                    'select id,humanId,ltrim(role_id) as role_id,sn,`name` AS `名称`,ltrim(`level`) AS `等级`,ltrim(featureLevel) AS `特性等级`,ltrim(star - 1) AS `星级` FROM game_tap_thief_0 WHERE role_id in ' + condition)
    thiefListMap = groupby(thiefs, key=lambda x: x['role_id'])
    weapons = select(db,
                     'select id,humanId,ltrim(role_id) as role_id,sn,`name` AS `名称`,ltrim(`level`) AS `等级`,ltrim(remouldCount) AS `改造等级`,ltrim(star - 1) AS `星级` FROM game_tap_weapon_0 WHERE role_id in ' + condition)
    weaponListMap = groupby(weapons, key=lambda x: x['role_id'])
    coops = select(db,
                   'select id,humanId,ltrim(role_id) as role_id,sn,`name` AS `名称`,ltrim(`level`) AS `等级` FROM game_tap_coop_0 WHERE role_id in ' + condition)
    coopListMap = groupby(coops, key=lambda x: x['role_id'])
    db.close()

    data = []
    for tapData in tapDataList:
        if tapData['awakeLevel'] > 0:
            tapData['level'] = tapData['awakeLevel']
            tapData['level_rank'] = 1
        else:
            tapData['level_rank'] = 0
        data.append({'role_id': tapData['role_id'], 'role_name': tapData['role_name'], 'level': tapData['level'],
                     'level_rank': tapData['level_rank'], 'avatar_id': tapData['avatar_id'],
                     '头像框': tapData['头像框']})
    ret = sender.post(pathRole, {'data': data})
    print(ret.content)

    data = []
    for tapData in tapDataList:
        role_data = [{'field': '怪盗数量', 'value': tapData['怪盗数量']},
                     {'field': '人格面具', 'value': tapData['人格面具']},
                     {'field': '成就', 'value': tapData['成就']},
                     {'field': '心之海段位', 'value': tapData['心之海段位']},
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
                                                 'field_3': thief['星级'], 'field_4': thief['特性等级']}})
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
    ip = '10.148.154.24'
    postTapData(ip, 'persona5_88_tap_0', 10 * 24 * 60)
    postTapData(ip, 'persona5_88_tap_1', 10 * 24 * 60)

    ret = sender.post(pathCollectionFilter,
                      {'data': {'1': {'key_total': {'4': 14, '5': 19}}, '2': {'key_total': {'4': 36, '5': 40}}}})
    print(ret.content)
