import pymysql
from flask import Flask, request
from sqlalchemy import create_engine

import upload

engine0 = create_engine(
    "mysql+pymysql://root:Nsywl!@#$%^&123@10.148.154.122:3306/persona5_15_tap_0",
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)
engine1 = create_engine(
    "mysql+pymysql://root:Nsywl!@#$%^&123@10.148.154.122:3306/persona5_15_tap_1",
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)
app = Flask(__name__)


@app.route('/tap/getTapData')
def getTapData():
    userId = request.args.get('userId')
    engine = engine0
    tapData = select(engine,
                     'SELECT ltrim(role_id) AS role_id,role_name,`level`,thiefNum AS `怪盗数量`, personaNum AS `人格面具`, achievementNum AS `成就`,`rank` AS `心之海段位`,unionBossScore AS `公会Boss总分`,questName AS `玩家主线进度` FROM game_tap_human_0 WHERE role_id = ' + userId)
    if len(tapData) == 0:
        engine = engine1
        tapData = select(engine,
                         'SELECT ltrim(role_id) AS role_id,role_name,`level`,thiefNum AS `怪盗数量`, personaNum AS `人格面具`, achievementNum AS `成就`,`rank` AS `心之海段位`,unionBossScore AS `公会Boss总分`,questName AS `玩家主线进度` FROM game_tap_human_0 WHERE role_id = ' + userId)
    tapData = tapData[0]
    tapData['拥有怪盗信息'] = select(engine,
                                     'select id,humanId,role_id,sn,`name` AS `名称`,`level` AS `等级`,awakeLevel AS `觉醒等级`,star AS `星级` FROM game_tap_thief_0 WHERE role_id = ' + userId)
    tapData['拥有武器信息'] = select(engine,
                                     'select id,humanId,role_id,sn,`name` AS `名称`,`level` AS `等级`,remouldCount AS `改造等级`,star AS `星级` FROM game_tap_weapon_0 WHERE role_id = ' + userId)
    tapData['拥有协同者信息'] = select(engine,
                                       'select id,humanId,role_id,sn,`name` AS `名称`,`level` AS `等级` FROM game_tap_coop_0 WHERE role_id = ' + userId)
    return tapData


@app.route('/tap/postTapData')
def postTapData():
    ip = request.args.get('ip')
    database = request.args.get('database')
    minites = request.args.get('minites')
    upload.postTapData(ip, database, minites)


def select(engine, sql):
    conn = engine.raw_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql)
    rets = cursor.fetchall()
    return rets


app.run(host='0.0.0.0', port=8888)
