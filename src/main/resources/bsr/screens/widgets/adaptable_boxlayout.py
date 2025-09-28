from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder

Builder.load_file('screens/widgets/adaptable_boxlayout.kv')

class AdaptableBoxLayout(BoxLayout):
    
    def __init__(self,**kwargs):    
        super(AdaptableBoxLayout,self).__init__(**kwargs)   
        self.size_hint=(1, None)
        self.bind(minimum_height=self.setter('height'))
        self.orientation = 'vertical'
