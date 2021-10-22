"""basic Flask app - demo of using a variable in a route"""
from flask import Flask, render_template,  request, url_for, flash, redirect, send_from_directory

import os 
import pandas as pd
import sqlite3

from Approvisionnement import approvisionner
from Consultation import consulter_stock
from Vente import Vente

app = Flask(__name__)



@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=('GET', 'POST'))
def create():
    con = sqlite3.connect('Cave_A_Bieres.db')
    cur = con.cursor()
    liste_distrib = cur.execute('''SELECT NOM_DISTRI FROM DISTRIBUTEURS''').fetchall()
    liste_brasseries = cur.execute('''SELECT NOM_BRASSERIE FROM BRASSERIES''').fetchall()
    liste_bieres = cur.execute('''SELECT BIERE FROM STOCK''').fetchall()
    con.commit()
    con.close()
    if request.method == 'POST':
        
        nom = request.form['biere']
        distributeur = request.form['distri']
        brasserie = request.form['brass']
        quantite = request.form['quantite']
        prix_achat = request.form['prix_achat']
        prix_vente = request.form['prix_vente']

        if not nom:
            flash('Le nom est obligatoire!')
        else:
            approvisionner(nom, brasserie, distributeur, quantite, prix_achat, prix_vente)
            return redirect(url_for('index'))

    return render_template('create.html', bieres = liste_bieres, distributeurs = liste_distrib, brasseries = liste_brasseries)

@app.route('/stock', methods=('GET', 'POST'))
def stock():
    df_stock = consulter_stock()
    return render_template('stock.html', tables=[df_stock.to_html(classes='data')], titles=df_stock.columns.values)

@app.route('/facturation', methods=["GET","POST"])
def facturation():
    con = sqlite3.connect('Cave_A_Bieres.db')

    cur = con.cursor()

    get_liste_vendeurs = cur.execute('''SELECT NOM_VENDEUR FROM VENDEURS''').fetchall()
    liste_vendeurs = [vendeur for t in get_liste_vendeurs for vendeur in t]
    get_liste_bieres = cur.execute('''SELECT BIERE FROM STOCK WHERE QUANTITE > 0''').fetchall()
    liste_bieres= [biere for t in get_liste_bieres for biere in t]
    vendeur = ""
    total_quantite = 0
    total_prix = 0
    if request.method == 'POST' :
        liste_bieres = pd.DataFrame(columns=["Bière","Vendeur","Quantité","Prix_unitaire"])
        for input in request.form :
            row = request.form[input].split(";")
            liste_bieres = liste_bieres.append(pd.DataFrame([[row[2],row[3],int(row[0]), int(row[1])]], columns=["Bière","Vendeur","Quantité","Prix_unitaire"]))
        Vente(liste_bieres).MAJ_stock()
        facture = Vente(liste_bieres).editer_facture()
        print("facture : \n",facture.loc[facture["Bière"] == 'Total'])
        vendeur_init = request.form.get('nom_vendeur')
        vendeur = facture.loc[facture["Bière"] == 'Total']["Vendeur"].values[0]
        qte_init = request.form.get('qte_total')
        total_quantite = facture.loc[facture["Bière"] == 'Total']["Quantité"].values[0]
        prix_init = request.form.get('prix_total')
        total_prix = facture.loc[facture["Bière"] == 'Total']["Prix_total"].values[0]
        return {'nom_vendeur':vendeur, 'qte_total':total_quantite, 'prix_total':total_prix}
    return render_template('facture.html', liste_vendeurs = liste_vendeurs, liste_bieres = liste_bieres, nom_vendeur = vendeur, qte_totale=total_quantite, prix_total=total_prix)

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)