import pymysql

sql = "SELECT id FROM nsywl5_task_detail_main WHERE `version`= 227 and id IN (SELECT taskId FROM nsywl5_task_detail_tags WHERE tagsId = 86) AND id IN (SELECT taskId FROM nsywl5_task_logs WHERE taskVersion = 227 and accessType LIKE '%rework%');"

db = pymysql.connect(host='10.77.38.129', user='root', password='N2kH5lJVJLAHWObs',
                     database='lb_server')
cursor = db.cursor()
cursor.execute(sql)
rets = cursor.fetchall()
for ret in rets:
    print(ret)
db.close()
