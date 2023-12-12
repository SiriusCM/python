import os

import pandas
from sqlalchemy import create_engine

path = r'C:\Users\Administrator\Desktop\basic\config\config_csv\\'
engine = create_engine("mysql+pymysql://root:N2kH5lJVJLAHWObs@10.77.38.129:3306/persona5_conf")
files = os.listdir(path)
for file in files:
    df = pandas.read_csv(path + file, skiprows=[0, 1, 3])
    df.to_sql(file.lower(), con=engine, if_exists='replace', index=False)
