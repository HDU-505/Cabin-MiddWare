from .sett_item import SettItem
from kivy.lang import Builder

Builder.load_file('screens/widgets/sett_boolean.kv')

class SettBoolean(SettItem):

    def enable_something(self):
        pass
