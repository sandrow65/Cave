import sqlite3
import pandas as pd
from datetime import date


def consulter_stock() :

    today = date.today().strftime('%Y%m%d')

    con = sqlite3.connect('Cave_A_Bieres.db')

    cur = con.cursor()

    stock_global = cur.execute('''SELECT * FROM STOCK''')
    col_names = list(map(lambda x: x[0], stock_global.description))
    col_names_to_display = col_names.copy()
    for i in range(len(col_names)):
        if col_names[i]=="DATE_CHGT":
            col_names_to_display[i] = "Date mise à jour"
        elif col_names[i]=="BIERE":
            col_names_to_display[i] = "Bière"
        elif col_names[i]=="BRASSERIE":
            col_names_to_display[i] = "Brasserie"
        elif col_names[i]=="DISTRIBUTEUR":
            col_names_to_display[i] = "Distributeur"
        elif col_names[i]=="QUANTITE":
            col_names_to_display[i] = "Quantité en stock"
        elif col_names[i]=="PRIX_ACHAT":
            col_names_to_display[i] = "Prix d'achat"
        elif col_names[i]=="PRIX_VENTE":
            col_names_to_display[i] = "Prix de vente"
        

    stock_global = pd.DataFrame(stock_global.fetchall())
    stock_global.columns = col_names
    stock_global.to_csv("stock/stock_%s.csv" %today, index = False)

    # reformate le tableau pour affichage
    stock_global["DATE_CHGT"] = pd.to_datetime(stock_global["DATE_CHGT"]).dt.strftime("%d %B %Y à %Hh%M")
    stock_global.columns = col_names_to_display

    con.commit()

    con.close()

    return stock_global

# consulter_stock()