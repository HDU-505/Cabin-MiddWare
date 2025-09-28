from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty,BooleanProperty,NumericProperty,ObjectProperty,ListProperty

class SettItem(FloatLayout):
    title = StringProperty('')
    desc = StringProperty(None, allownone=True)
    disabled = BooleanProperty(False)
    selected_alpha = NumericProperty(0.5)
    value = ObjectProperty(None)
    values = ListProperty(['0', '1'])
    options = ListProperty([])
    check_active = BooleanProperty(False)
