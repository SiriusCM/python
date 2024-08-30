import pymysql
from pymysql import cursors

ips_guan = ['10.148.154.122', '10.148.154.92', '10.148.154.47', '10.148.154.105', '10.148.154.54', '10.148.154.65',
            '10.148.154.127', '10.148.154.34', '10.148.154.52',
            '10.148.154.21', '10.148.154.111', '10.148.154.41', '10.148.154.117', '10.148.154.43', '10.148.154.19',
            '10.148.154.36', '10.148.154.33',
            '10.148.154.35', '10.148.154.38', '10.148.154.18', '10.148.154.31', '10.148.154.23', '10.148.154.45',
            '10.148.154.42', '10.148.154.48']

ips_qudao = ['10.148.157.22', '10.148.157.3', '10.148.157.44', '10.148.157.24', '10.148.157.15', '10.148.157.43',
             '10.148.157.16', '10.148.157.37', '10.148.157.14']

while True:
    print('please input sql:')
    sql = input()
    i = 0
    for ip in ips_guan:
        for j in range(0, 2):
            db = pymysql.connect(cursorclass=cursors.DictCursor, host=str(ip), user='root', password='Nsywl!@#$%^&123',
                                 database='persona5_88_game_' + str(i + j))
            cursor = db.cursor()
            cursor.execute(sql)
            rets = cursor.fetchall()
            for ret in rets:
                print(ret)
            db.close()
        i = i + 2
    i = 0
    for ip in ips_qudao:
        for j in range(0, 4):
            db = pymysql.connect(cursorclass=cursors.DictCursor, host=str(ip), user='root', password='Nsywl!@#$%^&123',
                                 database='persona5_66_game_' + str(i + j))
            cursor = db.cursor()
            cursor.execute(sql)
            rets = cursor.fetchall()
            for ret in rets:
                print(ret)
            db.close()
        i = i + 4
