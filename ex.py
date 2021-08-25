from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout


#######``Logics``#######
class Math(FloatLayout):
    def add(self):
        print(1+1)

#######``Windows``#######
class MainScreen(Screen):
    pass

class AnotherScreen(Screen):
   pass

class ScreenManagement(ScreenManager):
   pass


presentation = Builder.load_file("GUI_Style.kv")

class MainApp(App):
    def build(self):
       return presentation

if __name__ == "__main__":
    MainApp().run()