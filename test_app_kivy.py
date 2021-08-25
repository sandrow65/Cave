import pandas as pd

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup

from Approvisionnement import approvisionner
from Consultation import consulter_stock
from Vente import Vente

class MainApp(App):
    def build(self):
        layout = BoxLayout()

        button_approvisionner = Button(text='Approvisionner le stock',
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})
        button_approvisionner.bind(on_press=self.popup_saisie_approvisionnement)

        layout.add_widget(button_approvisionner)

        button_facture = Button(text='Facture',
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})
        button_facture.bind(on_press=self.popup_saisie_facture)

        layout.add_widget(button_facture)

        button_consulter = Button(text='Consulter le stock',
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})
        button_consulter.bind(on_press=self.on_press_button_consulter)

        layout.add_widget(button_consulter)

        return layout

    def popup_saisie_approvisionnement(self, instance):
        layout_approvisionner = GridLayout(cols = 2)
        layout_approvisionner.add_widget(Label(text='Nom de la bière :'))
        self.nom_biere = TextInput(multiline=False)
        layout_approvisionner.add_widget(self.nom_biere)

        layout_approvisionner.add_widget(Label(text='Distributeur :'))
        self.distributeur = TextInput(multiline=False)
        layout_approvisionner.add_widget(self.distributeur)

        layout_approvisionner.add_widget(Label(text='Quantité :'))
        self.quantite = TextInput(multiline=False, input_filter='int')
        layout_approvisionner.add_widget(self.quantite)

        layout_approvisionner.add_widget(Label(text="Prix d'achat :"))
        self.prix_achat = TextInput(multiline=False, input_filter='float')
        layout_approvisionner.add_widget(self.prix_achat)

        layout_approvisionner.add_widget(Label(text='Prix de vente :'))
        self.prix_vente = TextInput(multiline=False, input_filter='float')
        layout_approvisionner.add_widget(self.prix_vente)

        bouton_valider = Button(text='Valider la saisie')
        bouton_valider.bind(on_press=self.on_press_valider_approvisionnement)
        layout_approvisionner.add_widget(bouton_valider)

        bouton_retour = Button(text='Revenir au menu')
        bouton_retour.bind(on_press=self.on_press_retour)
        layout_approvisionner.add_widget(bouton_retour)

        print('You pressed the button!')
        self.popup = Popup(title='Approvisionnement du stock', 
                        content=layout_approvisionner)
        self.popup.bind()
        self.popup.open()
    
    def on_press_valider_approvisionnement(self, instance):
        print('Approvisionnement...')
        approvisionner(self.nom_biere.text, 
                        self.distributeur.text,
                        self.quantite.text, 
                        self.prix_achat.text, 
                        self.prix_vente.text)
        self.nom_biere.text = ""
        self.distributeur.text = ""
        self.quantite.text = ""
        self.prix_achat.text = ""
        self.prix_vente.text = ""

    def popup_saisie_facture(self, instance):

        self.facture = pd.DataFrame(columns=['Nom_biere, Quantite, Vendeur, Prix_unitaire'])

        layout_facture = GridLayout(cols = 2)
        layout_facture.add_widget(Label(text='Nom de la bière :'))
        self.nom_biere = TextInput(multiline=False)
        layout_facture.add_widget(self.nom_biere)

        layout_facture.add_widget(Label(text='Quantité :'))
        self.quantite = TextInput(multiline=False, input_filter='int')
        layout_facture.add_widget(self.quantite)

        layout_facture.add_widget(Label(text='Vendeur :'))
        self.vendeur = TextInput(multiline=False)
        layout_facture.add_widget(self.vendeur)

        layout_facture.add_widget(Label(text='Prix :'))
        self.prix_unitaire = TextInput(multiline=False, input_filter='float')
        layout_facture.add_widget(self.prix_unitaire)

        bouton_valider = Button(text='Ajouter à la facture')
        bouton_valider.bind(on_press=self.on_press_ajout_facture)
        layout_facture.add_widget(bouton_valider)

        bouton_retour = Button(text='Revenir au menu et éditer la facture')
        bouton_retour.bind(on_press=self.on_press_retour_valid_facture)
        layout_facture.add_widget(bouton_retour)

        print('You pressed the button!')
        self.popup = Popup(title='Edition de la facture', 
                        content=layout_facture)
        self.popup.bind()
        self.popup.open()
    
    def on_press_ajout_facture(self, instance):
        self.facture = self.facture.append(pd.DataFrame([self.nom_biere.text, self.quantite.text, self.vendeur.text, self.prix_unitaire.text], 
                            columns = self.facture.columns), ignore_index=True)

    def on_press_retour_valid_facture(self, instance):
        self.facture_finale = Vente(self.facture)
        self.facture_finale.MAJ_stock()
        self.facture_finale.editer_facture()
        self.popup.dismiss()

    def on_press_retour(self, instance):
        print("Fermeture de l'interface d'approvisionnement")
        self.popup.dismiss()

    def on_press_button_consulter(self, instance):
        print('You pressed the button!')
        consulter_stock()

if __name__ == '__main__':
    app = MainApp()
    app.run()
