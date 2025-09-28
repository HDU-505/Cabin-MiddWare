from kivy.uix.textinput import TextInput
from kivy.lang import Builder
import re

Builder.load_file('screens/widgets/ID_textinput.kv')

class IDTextInput(TextInput):
    
    pat = re.compile('[A-Za-z0-9]')
    
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if pat.match(substring):
            s = substring
        else:
            s = ''

        return super(IDTextInput, self).insert_text(s, from_undo=from_undo)
