from kivy.uix.screenmanager import Screen

from kivy.properties import StringProperty,ObjectProperty
from kivy.app import App

from datetime import datetime as dtime

from kivymd.app import MDApp
from kivymd.uix.card import MDCard

class HomeCard(MDCard):
    img_src= StringProperty('')
    btn_txt= StringProperty('')
    btn = ObjectProperty()

class Home(Screen):

    date = StringProperty(dtime.now().strftime("%A, %d %B %Y"))
    sr_btn = ObjectProperty()
    cal_btn = ObjectProperty()
    met_btn = ObjectProperty()
    gi_btn = ObjectProperty()
    fr_btn = ObjectProperty()
    set_btn = ObjectProperty()

    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)

    def close_app(self):
        pass

class HomeApp(MDApp):

    def __init__(self, **kwargs):
        super(HomeApp, self).__init__(**kwargs)

    def build(self):
        return Home()

if __name__ == '__main__':
    HomeApp().run()