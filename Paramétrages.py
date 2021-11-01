import sqlite3

def ajout_vendeur(nom_vendeur) : #
    print("nom vendeur : ", nom_vendeur)

    con = sqlite3.connect('Cave_A_Bieres.db')

    cur = con.cursor()

    max_idx = cur.execute('''SELECT MAX(IDX) FROM VENDEURS''').fetchone()[0]
    if max_idx is None:
        max_idx = 0

    params = [max_idx + 1, nom_vendeur]
    cur.execute("INSERT INTO VENDEURS VALUES (?, ?)", params)

    # Save (commit) the changes
    con.commit()

    print("Le vendeur a été ajouté")

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()