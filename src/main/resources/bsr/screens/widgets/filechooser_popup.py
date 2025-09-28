from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView

class FilechooserPopup(Popup):

    def __init__(self,popup_title,filechooser_rootpath,filechooser_filter,filechooser_multiselect,**kwargs):

        super(FilechooserPopup, self).__init__(**kwargs)
        
        self.title = popup_title
        self.content = BoxLayout(orientation='vertical', spacing=10, padding=15)

        self.separator_color=[float(233) / 255, float(147) / 255, float(34) / 255, 1]
        self.title_size="30dp"
        self.size_hint=(0.5, 0.5)
        self.background="images/blu_back.png"

        self.filechooser = FileChooserIconView(
            rootpath=filechooser_rootpath, filters=filechooser_filter,
            multiselect=filechooser_multiselect)

        self.content.add_widget(self.filechooser)

        self.done_btn = Button(size_hint_y=0.2, text='Load', font_size='40dp',
            bold= True, italic= True, background_color= [float(25)/255,float(63)/255,float(90)/255,0.4],color=[1,1,1,1])
        self.content.add_widget(self.done_btn)















