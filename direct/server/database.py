from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# MySQL配置
MYSQL_HOST = os.environ.get('MYSQL_HOST', '114.67.155.186')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'gaoliandi')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'twitter_clone')

DATABASE_URL = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4'

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()