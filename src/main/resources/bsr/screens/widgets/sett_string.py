from .sett_item import SettItem
from kivy.uix.popup import Popup

from kivy.lang import Builder
Builder.load_file('screens/widgets/sett_string.kv')

from screens.widgets.ID_textinput import IDTextInput
# from widgets.ID_textinput import IDTextInput

class SettStringPopup(Popup):
    pass

class SettString(SettItem):

    def create_popup(self):
        self.popup = SettStringPopup()
        self.popup.title = self.title
        self.popup.ok_btn.bind(on_release=self._validate)
        self.popup.open()
    
    def _validate(self, instance):
        self.popup.dismiss()
        value = self.popup.txt_input.text.strip()
        self.value = value
