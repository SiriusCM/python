import tkinter
from tkinter.messagebox import showinfo

import pandas
import pymysql
import sqlalchemy
import windnd


def dragged_files(files):
    msg = ''
    for file in files:
        file = file.decode('gbk')
        if '.xlsx' in file:
            for key in pandas.read_excel(file, sheet_name=None).keys():
                if '|' in key:
                    try:
                        key = str(key)
                        df = pandas.read_excel(file, sheet_name=key, skiprows=[0, 1, 3])
                        key = key.split("|")[1].lower()
                        df.to_sql(key, engine, if_exists='replace', index=False)
                    except:
                        print(key)
            msg += str(file)
            msg += '\n'
    showinfo('导入成功', msg)


pymysql.install_as_MySQLdb()
engine = sqlalchemy.create_engine('mysql://root:N2kH5lJVJLAHWObs@10.77.38.129:3306/excel')
tk = tkinter.Tk()
windnd.hook_dropfiles(tk, func=dragged_files)
tk.mainloop()
