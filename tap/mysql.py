import json
from itertools import groupby

import redis


def select_info(db, userId, humanId):
    baseMap = select(db, 'select name,level from game_human_base_0 where id = ' + humanId)
    questSnList = select(db,
                         'select questSn from game_human_quest_0 where humanId = ' + humanId + ' and state = 2')
    personaNum = select(db, 'select count(*) from game_human_persona_0 where humanId = ' + humanId)
    achievementNum = select(db, 'select count(*) from game_human_achievement_0 where humanId = ' + humanId)
    unionBossScore = select(db, 'select totalScore from game_human_union_boss_base_0 where id = ' + humanId)
    dcRankSn = select(db, 'select rankSn from game_human__d_c__base_info_0 where id = ' + humanId)

    thiefList = select(db,
                       'select id,humanId,sn,level as `等级`,awakeLevel as `觉醒等级` from game_human_thief_0 where humanId = ' + humanId)
    weaponList = select(db, '''SELECT game_human_weapon_0.humanId,game_human_weapon_0.id,game_human_weapon_0.sn,game_human_thief_0.weaponLevel AS `等级`,game_human_weapon_0.remouldCount AS `改造等级`
                    FROM game_human_weapon_0 LEFT JOIN game_human_thief_0 ON game_human_weapon_0.humanId = game_human_thief_0.humanId and game_human_thief_0.sn = game_human_weapon_0.thiefSn
                    WHERE game_human_weapon_0.humanId = ''' + humanId + ' and game_human_weapon_0.sn in ' + weapon_condition)
    coopList = select(db,
                      'select id,humanId,cooperatorSn as sn,level as `等级` from game_human_open_world_coop_0 where humanId = ' + humanId)

    confQuest = None
    for quest in questSnList:
        confQuest = ConfQuest[quest['questSn']]
        if confQuest.type == 1:
            break

    confChallengeRank = ConfChallengeRank[dcRankSn[0]['rankSn']]
    confRankRewardGroup = ConfRankRewardGroup[confChallengeRank.rankGroup]
    rank = redis_db.zrevrank('difficult_challenge_rank_list:110-' + str(confChallengeRank.rankLevel),
                             str(humanId))
    if rank is None:
        rank = '1等星1阶'
    else:
        rank = rank * 100 / eval('dc_card' + str(confChallengeRank.rankLevel))
        rank = int(rank)
        for confRankReward in confRankRewardGroup:
            if rank >= confRankReward.rankInterval0 and rank <= confRankReward.rankInterval1:
                rank = confRankReward.rankText
                break

    for thief in thiefList:
        confThief = ConfThief[thief['sn']]
        thief['名称'] = confThief.name
        thief['星级'] = confThief.gradeInitial
        del thief['humanId']

    for weapon in weaponList:
        if weapon['等级'] is None:
            weapon['等级'] = 1
        confWeapon = ConfWeapon[weapon['sn']]
        weapon['名称'] = confWeapon.name
        weapon['星级'] = confWeapon.quality
        del weapon['humanId']

    for coop in coopList:
        confCoop = ConfCoop[coop['sn']]
        coop['名称'] = confCoop.name
        del coop['humanId']

    data = {'role_id': userId, 'role_name': baseMap[0]['name'], 'level': baseMap[0]['level'],
            '怪盗数量': len(thiefList), '人格面具': personaNum[0]['count(*)'], '成就': achievementNum[0]['count(*)'],
            '心之海段位': rank,
            '公会Boss总分': unionBossScore[0]['totalScore'], '玩家主线进度': confQuest.name, '拥有怪盗信息': thiefList,
            '拥有武器信息': weaponList, '拥有协同者信息': coopList}
    return data


def select_role(db, condition, accounts):
    roles = select(db, 'select id,name as `role_name`,level from game_human_base_0 where id in ' + condition)
    for role in roles:
        role['role_id'] = accounts[role['id']]
        del role['id']
    body = {'data': roles}
    return body


def select_base(db, condition, accounts):
    quests = groupby(
        select(db, 'select humanId,questSn from game_human_quest_0 where humanId in ' + condition + ' and state = 2'),
        key=lambda x: x['humanId'])

    personaNumMap = {}
    for personaNum in select(db,
                             'select humanId,count(*) from game_human_persona_0 where humanId in ' + condition + ' group by humanId'):
        personaNumMap[personaNum['humanId']] = personaNum['count(*)']

    achievementNumMap = {}
    for achievementNum in select(db,
                                 'select humanId,count(*) from game_human_achievement_0 where humanId in ' + condition + ' group by humanId'):
        achievementNumMap[achievementNum['humanId']] = achievementNum['count(*)']

    thiefNumMap = {}
    for thiefNum in select(db,
                           'select humanId,count(*) from game_human_thief_0 where humanId in ' + condition + ' group by humanId'):
        thiefNumMap[thiefNum['humanId']] = thiefNum['count(*)']

    unionBossScoreMap = {}
    for unionBossScore in select(db,
                                 'select id,totalScore from game_human_union_boss_base_0 where id in ' + condition):
        unionBossScoreMap[unionBossScore['id']] = unionBossScore['totalScore']

    dcRankSnMap = {}
    for dcRankSn in select(db, 'select id,rankSn from game_human__d_c__base_info_0 where id in ' + condition):
        dcRankSnMap[dcRankSn['id']] = dcRankSn['rankSn']
    body = {}
    data = []
    body['type'] = 1
    body['data'] = data
    for questOnes in quests:
        humanId = questOnes[0]
        if humanId not in accounts:
            continue
        confQuest = None
        for quest in questOnes[1]:
            confQuest = ConfQuest[quest['questSn']]
            if confQuest.type == 1:
                break
        role_data = [{'field': '怪盗数量', 'value': str(thiefNumMap[humanId])},
                     {'field': '人格面具', 'value': str(personaNumMap[humanId])},
                     {'field': '成就', 'value': str(achievementNumMap[humanId])},
                     {'field': '玩家主线进度', 'value': confQuest.name}]
        if humanId in unionBossScoreMap:
            role_data.append({'field': '公会Boss总分', 'value': str(unionBossScoreMap[humanId])})
        else:
            role_data.append({'field': '公会Boss总分', 'value': '0'})
        if humanId in dcRankSnMap:
            confChallengeRank = ConfChallengeRank[dcRankSnMap[humanId]]
            confRankRewardGroup = ConfRankRewardGroup[confChallengeRank.rankGroup]
            rank = redis_db.zrevrank('difficult_challenge_rank_list:110-' + str(confChallengeRank.rankLevel),
                                     str(humanId))
            if rank is None:
                rank = '1等星1阶'
            else:
                rank = rank * 100 / eval('dc_card' + str(confChallengeRank.rankLevel))
                rank = int(rank)
                for confRankReward in confRankRewardGroup:
                    if rank >= confRankReward.rankInterval0 and rank <= confRankReward.rankInterval1:
                        rank = confRankReward.rankText
                        break
            role_data.append({'field': '心之海段位', 'value': rank})
        else:
            role_data.append({'field': '心之海段位', 'value': '1等星1阶'})
        data.append({'role_id': accounts[humanId], 'role_data': role_data})
    return body


def select_thief(db, condition, accounts):
    thiefs = select(db,
                    'select humanId,id,sn,level as `field_2`,awakeLevel as `field_3` from game_human_thief_0 where humanId in ' + condition)
    body = {}
    data = []
    body['type'] = 1
    body['data'] = data
    thiefs = groupby(thiefs, key=lambda x: x['humanId'])
    for thiefOnes in thiefs:
        humanId = thiefOnes[0]
        if humanId not in accounts:
            continue
        role_data = []
        data.append({'role_id': accounts[humanId], 'role_data': role_data})
        for thief in thiefOnes[1]:
            role_data.append({'id': thief['id'], 'sn': thief['sn'], 'optional_field': thief})
            confThief = ConfThief[thief['sn']]
            thief['field_1'] = confThief.name
            thief['field_2'] = str(thief['field_2'])
            thief['field_3'] = str(thief['field_3'])
            thief['field_4'] = str(confThief.gradeInitial)
            del thief['humanId']
            del thief['id']
            del thief['sn']
    return body


def select_weapon(db, condition, accounts):
    weapons = select(db, '''select game_human_weapon_0.humanId,game_human_weapon_0.id,game_human_weapon_0.sn,game_human_thief_0.weaponLevel as 'field_2',
                game_human_weapon_0.remouldCount as 'field_4' from game_human_weapon_0 left join game_human_thief_0 on game_human_weapon_0.humanId = game_human_thief_0.humanId 
                and game_human_thief_0.sn = game_human_weapon_0.thiefSn where game_human_weapon_0.humanId in ''' + condition + ' and game_human_weapon_0.sn in ' + weapon_condition)
    body = {}
    data = []
    body['type'] = 2
    body['data'] = data
    weapons = groupby(weapons, key=lambda x: x['humanId'])
    for weaponOnes in weapons:
        humanId = weaponOnes[0]
        if humanId not in accounts:
            continue
        role_data = []
        data.append({'role_id': accounts[humanId], 'role_data': role_data})
        for weapon in weaponOnes[1]:
            role_data.append({'id': weapon['id'], 'sn': weapon['sn'], 'optional_field': weapon})
            if weapon['field_2'] is None:
                weapon['field_2'] = 1
            confWeapon = ConfWeapon[weapon['sn']]
            weapon['field_1'] = confWeapon.name
            weapon['field_2'] = str(weapon['field_2'])
            weapon['field_3'] = str(confWeapon.quality)
            weapon['field_4'] = str(weapon['field_4'])
            del weapon['humanId']
            del weapon['id']
            del weapon['sn']
    return body


def select_coop(db, condition, accounts):
    coops = select(db,
                   'select humanId,id,cooperatorSn as sn,level as `field_2` from game_human_open_world_coop_0 where humanId in ' + condition)
    body = {}
    data = []
    body['type'] = 1
    body['data'] = data
    coops = groupby(coops, key=lambda x: x['humanId'])
    for coopOnes in coops:
        humanId = coopOnes[0]
        if humanId not in accounts:
            continue
        role_data = []
        data.append({'role_id': accounts[humanId], 'role_data': role_data})
        for coop in coopOnes[1]:
            role_data.append({'id': coop['id'], 'sn': coop['sn'], 'optional_field': coop})
            confCoop = ConfCoop[coop['sn']]
            coop['field_1'] = confCoop.name
            coop['field_2'] = str(coop['field_2'])
            del coop['humanId']
            del coop['id']
            del coop['sn']
    return body


def select(db, sql):
    cursor = db.cursor()
    cursor.execute(sql)
    rets = cursor.fetchall()
    return rets


def load_conf(file_name):
    confs = {}
    fp = open(file=file_name, encoding='utf-8')
    for data in json.load(fp):
        conf = Conf()
        for datum in data:
            setattr(conf, datum, data[datum])
        confs[data['sn']] = conf
    return confs


class Conf:
    pass


ConfQuest = load_conf('ConfQuest.json')
ConfThief = load_conf('ConfThief.json')
ConfWeapon = load_conf('ConfWeapon.json')
ConfCoop = load_conf('ConfCoop.json')
ConfChallengeRank = load_conf('ConfChallengeRank.json')
ConfRankReward = load_conf('ConfRankReward.json')

weapon_condition = '('
for sn in ConfWeapon:
    confWeapon = ConfWeapon[sn]
    if confWeapon.quality == 5 or confWeapon.quality == 6:
        weapon_condition = weapon_condition + str(sn) + ','
weapon_condition = weapon_condition[0:- 1] + ')'

ConfRankRewardGroup = {}
for sn in ConfRankReward:
    confRankReward = ConfRankReward[sn]
    if confRankReward.rankGroup not in ConfRankRewardGroup:
        ConfRankRewardGroup[confRankReward.rankGroup] = []
    r = str(confRankReward.rankInterval).split(',')
    if len(r) == 1:
        r = ['0', '1']
    setattr(confRankReward, 'rankInterval0', int(r[0]))
    setattr(confRankReward, 'rankInterval1', int(r[1]))
    ConfRankRewardGroup[confRankReward.rankGroup].append(confRankReward)

redis_db = redis.Redis(host='10.77.38.188', port=10479, password='Jpu2COnXTI43lWi1')
dc_card1 = redis_db.zcard('difficult_challenge_rank_list:110-1')
dc_card2 = redis_db.zcard('difficult_challenge_rank_list:110-2')
dc_card3 = redis_db.zcard('difficult_challenge_rank_list:110-3')
dc_card4 = redis_db.zcard('difficult_challenge_rank_list:110-4')
dc_card5 = redis_db.zcard('difficult_challenge_rank_list:110-5')
dc_card6 = redis_db.zcard('difficult_challenge_rank_list:110-6')
dc_card7 = redis_db.zcard('difficult_challenge_rank_list:110-7')
dc_card8 = redis_db.zcard('difficult_challenge_rank_list:110-8')
