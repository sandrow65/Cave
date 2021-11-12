import sqlite3
import pandas as pd
from datetime import date
import numpy as np
from datetime import datetime
sqlite3.register_adapter(np.int64, lambda val: int(val))
sqlite3.register_adapter(np.int32, lambda val: int(val))


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

def consulter_histo_ventes() :

    con = sqlite3.connect('Cave_A_Bieres.db')

    cur = con.cursor()

    get_histo_ventes = pd.DataFrame(cur.execute('''SELECT * FROM HISTO_VENTES''').fetchall(), columns=["IDX","N° de la facture","Date de la vente","Vendeur","Bière","Quantité","Prix de vente"]).drop(columns=["IDX"])
    get_histo_ventes["Prix total"] = get_histo_ventes["Prix de vente"] * get_histo_ventes["Quantité"]
    get_histo_ventes["Date de la vente"] = pd.to_datetime(get_histo_ventes["Date de la vente"]).dt.strftime("%d %B %Y à %Hh%M")
    con.commit()

    con.close()

    return get_histo_ventes

def faire_inventaire(df):
# df : dataframe des bières avec quantité théorique et réelle
    con = sqlite3.connect('Cave_A_Bieres.db')

    cur = con.cursor()

    # récupération des derniers idx utilisés
    max_id_inventaire = cur.execute('''SELECT MAX(ID_invent) FROM INVENTAIRES''').fetchone()[0]
    max_idx = cur.execute('''SELECT MAX(IDX) FROM INVENTAIRES''').fetchone()[0]
    if max_idx is None:
        max_idx = 0
    if max_id_inventaire is None:
        max_id_inventaire = 0
    max_idx = int(max_idx)
    max_id_inventaire = int(max_id_inventaire)

    print("Ajout de l'inventaire et mise à jour du stock...\n")

    df["IDX"] = pd.Series([max_idx + i for i in range(1, len(df)+1)], index= df.index)
    df["ID_Inventaire"] = pd.Series((max_id_inventaire + 1)*np.ones(len(df), dtype = np.int32),index=df.index)

    inventaire_liste = list(df.to_records(index=False))
    for i in range(len(inventaire_liste)):
        params_insert = [inventaire_liste[i][6], inventaire_liste[i][7], datetime.now(), "", inventaire_liste[i][1], inventaire_liste[i][4], inventaire_liste[i][5]]
        # Ajout lignes dans INVENTAIRE
        sql = cur.execute("INSERT INTO INVENTAIRES VALUES (?, ?, ?, ?, ?, ?, ?)", params_insert)
        # Mise à jour du stock réel dans STOCK
        params_update = [datetime.now(), inventaire_liste[i][5], inventaire_liste[i][1]]
        sql = cur.execute("UPDATE STOCK SET DATE_CHGT = ?, QUANTITE = ? WHERE BIERE = ? ", params_update)

    print("L'inventaire a été ajouté et le stock mis à jour.\n")
    con.commit()
    con.close()