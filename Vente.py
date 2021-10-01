import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
sqlite3.register_adapter(np.int64, lambda val: int(val))
sqlite3.register_adapter(np.int32, lambda val: int(val))

class Vente():

    def __init__(self, liste_bieres):
        self.liste_bieres = liste_bieres
        self.con = sqlite3.connect('Cave_A_Bieres.db')

        self.cur = self.con.cursor()

        self.max_id_facture = self.cur.execute('''SELECT MAX(ID_facture) FROM HISTO_VENTES''').fetchone()[0]
        self.max_idx = self.cur.execute('''SELECT MAX(IDX) FROM HISTO_VENTES''').fetchone()[0]
        if self.max_idx is None:
            self.max_idx = 0
        if self.max_id_facture is None:
            self.max_id_facture = 0
        self.max_id_facture = int(self.max_id_facture)
        self.max_idx = int(self.max_idx)

    def MAJ_stock(self):

        print("Mise à jour du stock...")

        
        self.liste_bieres["IDX"] = pd.Series([self.max_idx + i for i in range(1, len(self.liste_bieres)+1)], index= self.liste_bieres.index)
        self.liste_bieres["ID_facture"] = pd.Series((self.max_id_facture + 1)*np.ones(len(self.liste_bieres), dtype = np.int32),index=self.liste_bieres.index)

        ventes_facture = list(self.liste_bieres.to_records(index=False))
        for i in range(len(ventes_facture)):
            params_insert = [ventes_facture[i][4], ventes_facture[i][5], datetime.now(), ventes_facture[i][1], ventes_facture[i][0], ventes_facture[i][2], ventes_facture[i][3]]
            # Ajout lignes dans HISTO_VENTES
            sql = self.cur.execute("INSERT INTO HISTO_VENTES VALUES (?, ?, ?, ?, ?, ?, ?)", params_insert)
            # Mise à jour du stock restant dans STOCK
            params_update = [datetime.now(), ventes_facture[i][2], ventes_facture[i][0]]
            sql = self.cur.execute("UPDATE STOCK SET DATE_CHGT = ?, QUANTITE = QUANTITE - ? WHERE BIERE = ? ", params_update)

        print("Le stock a été mis à jour.\n")
        self.con.commit()
        self.con.close()

    def editer_facture(self):

        print("Edition de la facture...")

        vendeur = self.liste_bieres["Vendeur"]
        self.liste_bieres["Prix_total"] =  self.liste_bieres["Quantité"]*self.liste_bieres["Prix_unitaire"]
        self.liste_bieres = self.liste_bieres.drop(columns=["IDX","ID_facture"])
        total_quantite = sum(self.liste_bieres["Quantité"])
        total_prix = sum(self.liste_bieres["Prix_total"])

        self.liste_bieres = self.liste_bieres.append(pd.DataFrame([["Total", vendeur.values[0], total_quantite, '', total_prix]], columns = self.liste_bieres.columns))

        self.liste_bieres.to_csv("Facture_"+str(self.max_id_facture)+".csv", index=False)

        print("La facture a été éditée.\n")

        self.con.commit()

        self.con.close()

        return self.liste_bieres

    

