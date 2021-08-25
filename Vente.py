import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

class Vente():

    def __init__(self, liste_bieres):
        self.liste_bieres = liste_bieres
        self.con = sqlite3.connect('Cave_A_Bieres.db')

        self.cur = self.con.cursor()

        self.now = datetime.now()
        self.max_id_facture = self.cur.execute('''SELECT MAX(ID_facture) FROM HISTO_VENTES''').fetchone()[0]
        self.max_idx = self.cur.execute('''SELECT MAX(IDX) FROM HISTO_VENTES''').fetchone()[0]
        if self.max_idx is None:
            self.max_idx = 0
        if self.max_id_facture is None:
            self.max_id_facture = 0

    def MAJ_stock(self):

        print("Mise à jour du stock...\n")

        self.liste_bieres["IDX"] = pd.Series([self.max_idx + i for i in range(1, len(self.liste_bieres)+1)], index= self.liste_bieres.index)
        self.liste_bieres["ID_facture"] = pd.Series((self.max_id_facture + 1)*np.ones(len(self.liste_bieres)),index=self.liste_bieres.index)

        ventes_facture = list(self.liste_bieres.to_records(index=False))
        print(ventes_facture)

        sql = self.cur.execute("INSERT INTO HISTO_VENTES VALUES (?, ?, ?, ?, ?, ?)", ventes_facture)

        self.con.commit()

        self.con.close()


    def editer_facture(self):

        print("Edition de la facture...\n")

        vendeur = self.liste_bieres["Vendeur"]
        self.liste_bieres["Prix_total"] =  self.liste_bieres["Quantité"]*self.liste_bieres["Prix_unitaire"]
        total_quantite = sum(self.liste_bieres["Quantité"])
        total_prix = sum(self.liste_bieres["Prix_total"])

        self.liste_bieres = self.liste_bieres.append(pd.DataFrame([["Total", vendeur.values[0], total_quantite, '', total_prix]], columns = self.liste_bieres.columns))

        self.liste_bieres.to_csv("Facture_"+str(self.max_id_facture)+".csv", index=False)

        self.con.commit()

        self.con.close()

        return self.liste_bieres

    

