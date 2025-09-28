from kivy.uix.popup import Popup
from kivy.properties import StringProperty,ColorProperty

from kivy.lang import Builder
Builder.load_file('screens/widgets/confirm_popup.kv')

class ConfirmPopup(Popup):
    text = StringProperty('Do you really want to stop recording?')
    ok_text = StringProperty('Yes')
    cancel_text = StringProperty('No')
    label_color = ColorProperty()
    button_back_color = ColorProperty()

    __events__ = ('on_ok', 'on_cancel')

    def __init__(self, protocol,**kwargs):
        super(ConfirmPopup, self).__init__(**kwargs)
        orange = float(233)/255, float(147)/255, float(34)/255,1
        spearmint = (float(152)/255, float(215)/255, float(194)/255,1)

        if protocol == 'WAC2':
            self.background = "images/light_blu_back.png"
            self.label_color = spearmint
            self.button_back_color = (float(152)/255, float(215)/255, float(194)/255,0.1)
        else:
            self.background = "images/blu_back.png"
            self.label_color = orange
            self.button_back_color = (0,0,0.4,0.5)            


    def ok(self):
        self.dispatch('on_ok')
        self.dismiss()

    def cancel(self):
        self.dispatch('on_cancel')
        self.dismiss()

    def on_ok(self):
        pass

    def on_cancel(self):
        pass