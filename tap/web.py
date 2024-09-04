import pymysql
import redis
from flask import Flask, request
from pymysql import cursors

import mysql

ips = ['10.148.154.122', '10.148.154.92', '10.148.154.47', '10.148.154.105', '10.148.154.54', '10.148.154.65',
       '10.148.154.127', '10.148.154.34', '10.148.154.52',
       '10.148.154.21', '10.148.154.111', '10.148.154.41', '10.148.154.117', '10.148.154.43', '10.148.154.19',
       '10.148.154.36', '10.148.154.33',
       '10.148.154.35', '10.148.154.38', '10.148.154.18', '10.148.154.31', '10.148.154.23', '10.148.154.45',
       '10.148.154.42', '10.148.154.48']
ips = ['10.77.38.188']

redis_db = redis.Redis(host='10.77.38.188', port=10480, password='Jpu2COnXTI43lWi1')

app = Flask(__name__)

weaponCondition = mysql.weapon_condition
print(weaponCondition)


@app.route('/tap/getTapData')
def hello():
    userId = request.args.get('userId')
    humanId = redis_db.hget('userid2id', userId)
    humanId = humanId.decode()
    index = int(humanId) % 2
    db = pymysql.connect(cursorclass=cursors.DictCursor, host=ips[int(index / 2)], user='root',
                         password='N2kH5lJVJLAHWObs',
                         database='persona5_15_game_' + str(index))
    ret = mysql.select_info(db, userId, humanId)
    db.close()

    return ret


app.run(host='0.0.0.0', port=8888)
