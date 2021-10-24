import sqlite3


def creation_BDD() :

    con = sqlite3.connect('Cave_A_Bieres.db')

    cur = con.cursor()

    # Create table STOCK
    cur.execute('''DROP TABLE STOCK''')
    cur.execute('''CREATE TABLE STOCK
                (IDX integer primary key AUTOINCREMENT, 
                DATE_CHGT date, 
                BIERE text, 
                BRASSERIE text,
                DISTRIBUTEUR text, 
                QUANTITE integer, 
                PRIX_ACHAT real, 
                PRIX_VENTE real)''')

    # Create table VENTES
    cur.execute('''DROP TABLE HISTO_VENTES''')
    cur.execute('''CREATE TABLE HISTO_VENTES
                (IDX integer primary key AUTOINCREMENT, 
                ID_facture integer,
                DATE datetime, 
                VENDEUR text, 
                BIERE text,
                QUANTITE real, 
                PRIX real)''')

    # Create table VENDEURS
    cur.execute('''DROP TABLE VENDEURS''')
    cur.execute('''CREATE TABLE VENDEURS 
                (IDX integer, 
                NOM_VENDEUR text)''')
    cur.execute('''INSERT INTO VENDEURS VALUES (1, 'Sandra'), (2, 'Thierry')''')

    # Create table DISTRIBUTEURS
    cur.execute('''DROP TABLE DISTRIBUTEURS''')
    cur.execute('''CREATE TABLE DISTRIBUTEURS 
                (IDX integer, 
                NOM_DISTRI text)''')
    cur.execute('''INSERT INTO DISTRIBUTEURS VALUES (1, 'TestDistri1'), (2, 'TestDistri2'), (3,'TestDistri3')''')

    # Create table BRASSERIES
    cur.execute('''DROP TABLE BRASSERIES''')
    cur.execute('''CREATE TABLE BRASSERIES 
                (IDX integer, 
                NOM_BRASSERIE text)''')
    cur.execute('''INSERT INTO BRASSERIES VALUES (1, 'IRON'), (2, 'La débauche'), (3, 'La superbe'), (4, 'L Excuse')''')

    # Save (commit) the changes
    con.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    con.close()

creation_BDD()