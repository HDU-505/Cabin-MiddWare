from kivy.uix.popup import Popup
from kivy.properties import StringProperty

from kivy.lang import Builder
Builder.load_file('screens/widgets/warning_popup.kv')

class WarningPopup(Popup):
    lab_txt = StringProperty('')
