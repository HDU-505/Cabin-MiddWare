from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty,StringProperty

from kivy.lang import Builder
Builder.load_file('screens/widgets/progress_bar_layout.kv')
Builder.load_file('screens/widgets/orange_progress_bar.kv')


class ProgressBarLayout(FloatLayout):
    pb = ObjectProperty()
    pb_lab = ObjectProperty()
    info = StringProperty('')

    def __init__(self, **kwargs):
        super(ProgressBarLayout, self).__init__()
        self.background = "images/blu_back.png"
        self.pb.value = 0
