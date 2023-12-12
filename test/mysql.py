import pymysql

conn = pymysql.connect(
    host='10.77.38.129',
    user='root',
    password='N2kH5lJVJLAHWObs',
    database='lb_server'
)

cursor = conn.cursor()
sql = 'select * from aa_users'
cursor.execute(sql)
for i in cursor.fetchall():
    print(i)

conn.commit()
conn.close()
