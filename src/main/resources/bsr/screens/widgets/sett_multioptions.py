from .sett_options import SettOptions
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.core.window import Window

from kivy.lang import Builder
Builder.load_file('screens/widgets/sett_multioptions.kv')

class SettMultiOptionsPopup(Popup):
    ad_bl = ObjectProperty()
    done_btn = ObjectProperty()

class SettMultiOptions(SettOptions):

    def _set_option(self, instance):
        if instance.state == 'down':
            self.opt_list.append(instance.text)
        elif instance.state == 'normal' and instance.text in self.opt_list:
            self.opt_list.remove(instance.text)

    def create_popup(self):

        # create the popup
        popup_width = min(0.95 * Window.width, dp(500))
        popup_height = min(0.95 * Window.width, dp(600))
        if len(self.options)*dp(55)+dp(45)+dp(55) < popup_height:
            popup_height = (len(self.options))*dp(55)+dp(45)+dp(120)

        self.popup = SettMultiOptionsPopup()
        self.popup.title = self.title
        self.popup.width = popup_width
        self.popup.height = popup_height
        
        # add all the options
        for option in self.options:
            btn = ToggleButton(text=option, state='normal',font_size = dp(25),size_hint_y = None,height=dp(55))
            btn.bind(on_release=self._set_option)
            self.popup.ad_bl.add_widget(btn)

        # finally, add a cancel button to return on the previous panel
        self.popup.done_btn.bind(on_release=self.close_popup)

        # and open the popup !
        self.opt_list = []
        self.popup.open()

    def close_popup(self, instance):
        str = ','
        self.value = str.join(self.opt_list)
        self.popup.dismiss()
