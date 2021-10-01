import sqlite3
import pandas as pd
from datetime import date

def consulter_stock() :

    today = date.today().strftime('%Y%m%d')

    con = sqlite3.connect('Cave_A_Bieres.db')

    cur = con.cursor()

    stock_global = cur.execute('''SELECT * FROM STOCK''')
    col_names = list(map(lambda x: x[0], stock_global.description))

    stock_global = pd.DataFrame(stock_global.fetchall())
    stock_global.columns = col_names

    print(stock_global)

    stock_global.to_csv("stock_%s.csv" %today, index = False)

    con.commit()

    con.close()

    return stock_global

# consulter_stock()