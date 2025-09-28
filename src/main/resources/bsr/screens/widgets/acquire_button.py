from kivy.uix.button import Button
from kivy.properties import ListProperty
from kivy.clock import Clock

from kivy.lang import Builder
Builder.load_file('screens/widgets/acquire_button.kv')

class AcquireButton(Button):
    
    back_color = ListProperty([]) 

    def __init__(self,**kwargs):
        super(AcquireButton,self).__init__(**kwargs)
        self.back_color= [float(25)/255,float(63)/255,float(90)/255,1] #[74/255, 133/255, 33/255,0.2] 
        
    def pressed_effect(self):
        self.back_color =  (self.back_color[0],self.back_color[1],self.back_color[2],0.6)
        Clock.schedule_once(self.back_to_normal,0.2)

    def back_to_normal(self,dt):
        self.back_color =  (self.back_color[0],self.back_color[1],self.back_color[2],1)