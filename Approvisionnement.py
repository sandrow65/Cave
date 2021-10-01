import sqlite3
from datetime import date

def approvisionner(nom_biere, brasserie, distributeur, quantite, prix_achat, prix_vente) : #

    con = sqlite3.connect('Cave_A_Bieres.db')

    cur = con.cursor()

    today = date.today()

    max_idx = cur.execute('''SELECT MAX(IDX) FROM STOCK''').fetchone()[0]
    if max_idx is None:
        max_idx = 0
    print(max_idx)

    bieres_existantes = cur.execute('''SELECT BIERE FROM STOCK''').fetchall()
    bieres_existantes = [b[0] for b in bieres_existantes]
    print("Bières existantes : \n",bieres_existantes, nom_biere in bieres_existantes)

    if nom_biere in bieres_existantes :
        # La bière existe déjà dans le stock
        params = [today, quantite, nom_biere]
        cur.execute('''UPDATE STOCK SET DATE_CHGT = ?, QUANTITE = QUANTITE + ? WHERE BIERE = ?''', params)
    else :
        # Nouveau stock
        params = [max_idx+1, today, nom_biere, brasserie, distributeur, quantite, prix_achat, prix_vente]
        cur.execute("INSERT INTO STOCK VALUES (?, ?, ?, ?, ?, ?, ?, ?)", params)

    # Save (commit) the changes
    con.commit()

    print("Les changements ont été effectués")

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()


# approvisionner()