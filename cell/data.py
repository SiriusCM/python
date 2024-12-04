import redis
from pymysql.cursors import DictCursor
from sqlalchemy import create_engine

redis_db = redis.Redis(host='10.77.38.129', port=6379, password='N2kH5lJVJLAHWObs')

engine = create_engine(
    "mysql+pymysql://root:N2kH5lJVJLAHWObs@10.77.38.188:3306/persona5_15_game_0",
    max_overflow=0,  # 超过连接池大小外最多创建的连接
    pool_size=5,  # 连接池大小
    pool_timeout=30,  # 池中没有线程最多等待的时间，否则报错
    pool_recycle=-1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
)


def execute(sql):
    conn = engine.raw_connection()
    cursor = conn.cursor(DictCursor)
    cursor.execute(sql)
    rets = cursor.fetchall()
    return rets
