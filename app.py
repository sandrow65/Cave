"""basic Flask app - demo of using a variable in a route"""
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory

import os 
import pandas as pd
import sqlite3

from Approvisionnement import approvisionner
from Consultation import consulter_stock, consulter_histo_ventes, faire_inventaire
from Vente import Vente, notes_enregistrees, recup_detail_note, supprimer_note
from Paramétrages import ajout_vendeur

import locale

locale.setlocale(locale.LC_ALL, 'fr_FR.utf-8')


app = Flask(__name__)
app.templates_auto_reload = True

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

@app.route('/administration/stock', methods=('GET', 'POST'))
def stock():
    con = sqlite3.connect('Cave_A_Bieres.db')
    cur = con.cursor()
    df_stock = consulter_stock().drop(columns="IDX")
    # liste des bières pour le dropdown
    get_liste_bieres = cur.execute('''SELECT BIERE FROM STOCK WHERE QUANTITE > 0''').fetchall()
    liste_bieres = [biere for t in get_liste_bieres for biere in t]
    # liste des brasseries pour le dropdown
    get_liste_brass = cur.execute('''SELECT DISTINCT BRASSERIE FROM STOCK WHERE QUANTITE > 0''').fetchall()
    liste_brasseries = [brass for t in get_liste_brass for brass in t]
    con.commit()
    con.close()
    return render_template('stock.html', tables=[df_stock.to_html(classes='data')], titles=df_stock.columns.values, \
        liste_bieres=liste_bieres, liste_brasseries = liste_brasseries)

@app.route('/facturation', methods=["GET","POST"])
def facturation():
    con = sqlite3.connect('Cave_A_Bieres.db')
    cur = con.cursor()

    # liste des vendeurs pour le dropdown
    get_liste_vendeurs = cur.execute('''SELECT NOM_VENDEUR FROM VENDEURS''').fetchall()
    liste_vendeurs = [vendeur for t in get_liste_vendeurs for vendeur in t]
    # liste des bières pour le dropdown
    get_liste_bieres = cur.execute('''SELECT BIERE FROM STOCK WHERE QUANTITE > 0''').fetchall()
    liste_bieres = [biere for t in get_liste_bieres for biere in t]
    # prix de la première bière pour affichage
    prix_init = cur.execute('''SELECT PRIX_VENTE FROM STOCK WHERE QUANTITE > 0''').fetchone()[0]
    liste_bieres_df = pd.DataFrame(columns=["Bière","Vendeur","Quantité","Prix_unitaire"])
    vendeur = ""
    total_quantite = 0
    total_prix = 0
    prix_biere = 0
    if request.method == 'POST' :
        item_sent = list(request.form.to_dict().values())[0]
        if item_sent in liste_bieres:
            prix_biere = cur.execute('''SELECT PRIX_VENTE FROM STOCK WHERE BIERE = ?''', [item_sent]).fetchone()[0]
            return {'prix_unit' : prix_biere}
        else :
            l = len(request.form.to_dict())
            d = request.form.to_dict()
            print("d init : ", d)
            type = d.pop("r"+str(l-1)) #récupérer s'il s'agit d'un submit ou d'un save
            nom_note = d.pop("r"+str(l-2)) #récupérer le nom de la note si c'est un enregistrement et vide si paiement
            for input in d :
                row = request.form[input].split(";")
                print(row)
                liste_bieres_df = liste_bieres_df.append(pd.DataFrame([[row[2],row[3],int(row[0]), float(row[1])]], columns=["Bière","Vendeur","Quantité","Prix_unitaire"]))
            if type == "submit":
                # ok paiement on met à jour le stock et fait la facture
                Vente(liste_bieres_df).MAJ_stock()
                facture = Vente(liste_bieres_df).editer_facture()
                print("facture : \n",facture.loc[facture["Bière"] == 'Total'])
                vendeur_init = request.form.get('nom_vendeur')
                vendeur = facture.loc[facture["Bière"] == 'Total']["Vendeur"].values[0]
                total_quantite = facture.loc[facture["Bière"] == 'Total']["Quantité"].values[0]
                total_prix = facture.loc[facture["Bière"] == 'Total']["Prix_total"].values[0]
                return {'nom_vendeur':vendeur, 'qte_total':total_quantite, 'prix_total':total_prix}
            elif type == "save":
                # ko on fait une note à payer plus tard
                print("à enregistrer\n")
                print("nom note : ", nom_note)
                print(liste_bieres_df)
                Vente(liste_bieres_df).enregistrer(nom_note)
    return render_template('facture.html', liste_vendeurs = liste_vendeurs, liste_bieres = liste_bieres, \
        nom_vendeur = vendeur, qte_totale=total_quantite, prix_total=total_prix, prix_unit=prix_biere, prix_init = prix_init)

@app.route('/facturation/notes', methods=["GET","POST"])
def liste_notes() :
    liste_notes = notes_enregistrees()
    if request.method == "POST":
        note = list(request.form.to_dict().values())[0]
        return redirect(url_for('detail', note = str(note)))
    else :
        return render_template('liste_notes.html', notes = [l[0] for l in liste_notes])
    # return render_template('liste_notes.html', notes = [l[2] for l in liste_notes])

@app.route('/facturation/notes/detail/<note>', methods = ["GET","POST"])
@app.route('/facturation/notes/detail', defaults={'note': None}) 
def detail(note):
    print("à finir")
    con = sqlite3.connect('Cave_A_Bieres.db')

    cur = con.cursor()

    # liste des vendeurs pour le dropdown
    get_liste_vendeurs = cur.execute('''SELECT NOM_VENDEUR FROM VENDEURS''').fetchall()
    liste_vendeurs = [vendeur for t in get_liste_vendeurs for vendeur in t]
    # liste des bières pour le dropdown
    get_liste_bieres = cur.execute('''SELECT BIERE FROM STOCK WHERE QUANTITE > 0''').fetchall()
    liste_bieres = [biere for t in get_liste_bieres for biere in t]
    # prix de la première bière pour affichage
    prix_init = cur.execute('''SELECT PRIX_VENTE FROM STOCK WHERE QUANTITE > 0''').fetchone()[0]

    liste_bieres_df = pd.DataFrame(columns=["Bière","Vendeur","Quantité","Prix_unitaire"])

    detail_note, vendeur, total_qte, prix_total = recup_detail_note(note)
    liste_bieres_df = liste_bieres_df.append(detail_note[["Bière","Vendeur","Quantité","Prix_unitaire"]])
    print(liste_bieres_df)
    if request.method == 'POST' :
        item_sent = list(request.form.to_dict().values())[0]
        print(item_sent)
        if item_sent in liste_bieres:
            prix_biere = cur.execute('''SELECT PRIX_VENTE FROM STOCK WHERE BIERE = ?''', [item_sent]).fetchone()[0]
            return {'prix_unit' : prix_biere}
        else :
            l = len(request.form.to_dict())
            d = request.form.to_dict()
            print("d init : ", d)
            type = d.pop("r"+str(l-1)) #récupérer s'il s'agit d'un submit ou d'un save
            nom_note = d.pop("r"+str(l-2)) #récupérer le nom de la note si c'est un enregistrement et vide si paiement
            for input in d :
                row = request.form[input].split(";")
                if row != [''] :
                    liste_bieres_df = liste_bieres_df.append(pd.DataFrame([[row[2],row[3],int(row[0]), float(row[1])]], columns=["Bière","Vendeur","Quantité","Prix_unitaire"]))
            if type == "submit":
                # ok paiement on met à jour le stock et fait la facture
                Vente(liste_bieres_df).MAJ_stock()
                facture = Vente(liste_bieres_df).editer_facture()
                # on supprime la note en base de données
                supprimer_note(note)
                print("facture : \n",facture.loc[facture["Bière"] == 'Total'])
                vendeur_init = request.form.get('nom_vendeur')
                vendeur = facture.loc[facture["Bière"] == 'Total']["Vendeur"].values[0]
                total_quantite = facture.loc[facture["Bière"] == 'Total']["Quantité"].values[0]
                total_prix = facture.loc[facture["Bière"] == 'Total']["Prix_total"].values[0]
                return {'nom_vendeur':vendeur, 'qte_total':total_quantite, 'prix_total':total_prix}
            elif type == "save":
                # ko on fait une note à payer plus tard
                print("à enregistrer\n")
                print("nom note : ", nom_note)
                print(liste_bieres_df)
                Vente(liste_bieres_df).enregistrer(nom_note)
    return render_template('note.html', nom_note = note, \
        detail_note = detail_note[["Bière","Vendeur","Quantité","Prix_unitaire"]].values, liste_vendeurs = liste_vendeurs, liste_bieres=liste_bieres, \
        nom_vendeur = vendeur, qte_totale = total_qte, prix_total = prix_total, prix_init=prix_init)

@app.route('/administration', methods=["GET","POST"])
def param():
    return render_template('admin.html')

@app.route('/administration/liste_vendeurs', methods=["GET","POST"])
def param_vendeurs():
    con = sqlite3.connect('Cave_A_Bieres.db')
    cur = con.cursor()

    get_liste_vendeurs = cur.execute('''SELECT NOM_VENDEUR FROM VENDEURS''').fetchall()
    liste_vendeurs = [vendeur for t in get_liste_vendeurs for vendeur in t]

    if request.method == "POST":
        new_vendeur = request.form['vendeur']
        ajout_vendeur(new_vendeur)
    return render_template('param_vendeurs.html', liste_vendeurs = liste_vendeurs)

@app.route('/administration/histo_ventes', methods=["GET","POST"])
def histo_ventes():

    ventes = consulter_histo_ventes()
    prix_total = str(sum(ventes["Prix total"])) + " €"
    qte_totale = str(sum(ventes["Quantité"])) + " bières"

    if request.method == "POST":
        facture = request.form['facture']
        biere = request.form['biere']
        vendeur = request.form['vendeur']
        date_min = request.form['date_min']
        date_max = request.form['date_max']
        if facture != "":
            print("facture")
            ventes = ventes.loc[ventes["N° de la facture"] == int(facture)]
        if biere != "" :
            print("biere")
            ventes = ventes.loc[ventes["Bière"] == biere]
        if vendeur != "" :
            print("vendeur")
            ventes = ventes.loc[ventes["Vendeur"] == vendeur]
        if date_min != "":
            print("date1")
            ventes = ventes.loc[pd.to_datetime(ventes["Date de la vente"], format = "%d %B %Y à %Hh%M") >= pd.to_datetime(date_min)]
        if date_max != "" :
            print("date2")
            ventes = ventes.loc[pd.to_datetime(ventes["Date de la vente"], format = "%d %B %Y à %Hh%M") <= pd.to_datetime(date_max)]
        prix_total = str(sum(ventes["Prix total"])) + " €"
        qte_totale = str(int(sum(ventes["Quantité"]))) + " bières"
    return render_template('histo_ventes.html', table_ventes = [ventes.to_html(classes='data')], total_prix = prix_total, total_qte = qte_totale)

@app.route('/administration/inventaire', methods=('GET', 'POST'))
def inventaire():
    con = sqlite3.connect('Cave_A_Bieres.db')
    cur = con.cursor()
    # liste des bières pour le dropdown
    get_liste_bieres = cur.execute('''SELECT BIERE FROM STOCK WHERE QUANTITE > 0''').fetchall()
    liste_bieres = [biere for t in get_liste_bieres for biere in t]
    # liste des brasseries pour le dropdown
    get_liste_brass = cur.execute('''SELECT DISTINCT BRASSERIE FROM STOCK WHERE QUANTITE > 0''').fetchall()
    liste_brasseries = [brass for t in get_liste_brass for brass in t]
    con.commit()
    con.close()

    df_inventaire = consulter_stock().drop(columns=["IDX","Prix d'achat","Prix de vente"])
    col_names = df_inventaire.columns
    col_names = ["Quantité théorique" if x == "Quantité en stock" else x for x in col_names]
    df_inventaire.columns = col_names
    df_inventaire["Quantité observée"] = df_inventaire["Quantité théorique"]
    if request.method == "POST" :
        print(list(request.form.to_dict().values()))
        df_inventaire_fait = df_inventaire.copy()
        df_inventaire_fait["Quantité observée"] = pd.Series(list(request.form.to_dict().values()))
        faire_inventaire(df_inventaire_fait)
    return render_template('inventaire.html', bieres=df_inventaire[["Bière","Quantité théorique"]].values, \
        liste_bieres = liste_bieres, liste_brasseries = liste_brasseries) # on envoie que le nom de la bière et les quantités théoriques

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)