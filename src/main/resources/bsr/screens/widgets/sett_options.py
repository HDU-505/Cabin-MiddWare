from .sett_item import SettItem
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.core.window import Window

from kivy.lang import Builder
Builder.load_file('screens/widgets/sett_options.kv')

class SettOptionsPopup(Popup):
    ad_bl = ObjectProperty()

class SettOptions(SettItem):

    popup = ObjectProperty()

    def _set_option(self, instance):
        self.value = instance.text
        self.popup.dismiss()

    def create_popup(self):
        # create the popup
        popup_width = min(0.95 * Window.width, dp(500))
        popup_height = min(0.95 * Window.width, dp(600))
        if len(self.options)*dp(55)+dp(45)+dp(55) < popup_height:
            popup_height = (len(self.options)+1)*dp(55)+dp(45)

        self.popup = SettOptionsPopup()
        self.popup.title = self.title
        self.popup.width = popup_width
        self.popup.height = popup_height

        # add all the options
        for option in self.options:
            btn = ToggleButton(text=option, state='normal',font_size = dp(25),size_hint_y = None,height=dp(55))
            btn.bind(on_release=self._set_option)
            self.popup.ad_bl.add_widget(btn)

        # and open the popup !
        self.popup.open()
