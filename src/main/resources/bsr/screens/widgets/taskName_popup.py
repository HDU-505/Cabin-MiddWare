from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.properties import ListProperty
from kivy.clock import Clock
from kivy.app import App

from kivy.lang import Builder
Builder.load_file('screens/widgets/taskName_popup.kv')

from screens.widgets.acquire_button import AcquireButton
# from widgets.acquire_button import AcquireButton
# from acquire_button import AcquireButton

class TaskName(ModalView):

    run_name = ''
    
    def set_run_name(self,txt):
        self.run_name = txt
        self.dismiss()

    def on_dismiss(self):
        pass
    
class TaskNameApp(App):
    def build(self):
        return TaskName()

if __name__ == '__main__':
    TaskNameApp().run()