from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty,ObjectProperty,StringProperty
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton

from kivy.lang import Builder
Builder.load_file('screens/widgets/sett_metric.kv')

class SettOptionsMetricPopup(Popup):
    ad_bl = ObjectProperty()

class SettMultiOptionsMetricPopup(Popup):
    ad_bl = ObjectProperty()
    done_btn = ObjectProperty()

class SettMetric(FloatLayout):
    metric_name = StringProperty('')
    check = ObjectProperty()
    method_btn = ObjectProperty()
    method_options = ListProperty(["Raw","Calibrated","Classifier"])
    method_popup = ObjectProperty()
    method_value = StringProperty('')
    
    feat_btn = ObjectProperty()
    feat_raw_options = ListProperty([])
    feat_cal_options = ListProperty([])
    feat_class_options = ListProperty([])
    feat_popup = ObjectProperty()
    feat_value = StringProperty('')
    
    ch_btn = ObjectProperty()
    ch_value = StringProperty('')
    ch_popup = ObjectProperty()
    ch_options = ListProperty([])
    ch_list_nr = ListProperty([])
    
    def open_method_popup(self):
        # create the popup
        popup_width = min(0.95 * Window.width, dp(500))
        popup_height = min(0.95 * Window.width, dp(600))
        if len(self.method_options)*dp(55)+dp(45)+dp(55) < popup_height:
            popup_height = (len(self.method_options)+1)*dp(55)+dp(45)

        self.method_popup = SettOptionsMetricPopup()
        self.method_popup.title = 'Metric Computation Method'
        self.method_popup.width = popup_width
        self.method_popup.height = popup_height

        # add all the options
        for option in self.method_options:
            btn = ToggleButton(text=option, state='normal',font_size = dp(25),size_hint_y = None,height=dp(55))
            btn.bind(on_release=self._set_method_option)
            self.method_popup.ad_bl.add_widget(btn)

        # and open the popup !
        self.method_popup.open()

    def _set_method_option(self,instance):
        self.method_value = instance.text
        self.feat_btn.disabled = False
        self.method_popup.dismiss()

    def open_feat_popup(self):

        # create the popup
        popup_width = min(0.95 * Window.width, dp(500))
        popup_height = min(0.95 * Window.width, dp(600))

        if self.method_value != 'Classifier':
            if self.method_value == 'Raw':
                self.feat_options = self.feat_raw_options
            elif self.method_value == 'Calibrated':
                self.feat_options = self.feat_cal_options
            if len(self.feat_options)*dp(55)+dp(45)+dp(55) < popup_height:
                popup_height = (len(self.feat_options)+1)*dp(55)+dp(45)
            self.feat_popup = SettOptionsMetricPopup()
            self.feat_popup.title = 'Select one Formula for computation'
        else:
            self.feat_options = self.feat_class_options                    
            if len(self.feat_options)*dp(55)+dp(45)+dp(55) < popup_height:
                popup_height = (len(self.feat_options))*dp(55)+dp(45)+dp(120)
            self.feat_popup = SettMultiOptionsMetricPopup()
            self.feat_popup.title = 'Select the features for the classifier'
            # finally, add a cancel button to return on the previous panel
            self.feat_popup.done_btn.bind(on_release=self.close_feat_popup)
            self.feat_list = []

        
        self.feat_popup.width = popup_width
        self.feat_popup.height = popup_height

        # add all the options
        for option in self.feat_options:
            btn = ToggleButton(text=option, state='normal',font_size = dp(25),size_hint_y = None,height=dp(55))
            btn.bind(on_release=self._set_feat_option)
            self.feat_popup.ad_bl.add_widget(btn)

        # and open the popup !
        self.feat_popup.open()

    def _set_feat_option(self, instance):
        if self.method_value == 'Classifier':
            if instance.state == 'down':
                self.feat_list.append(instance.text)
            elif instance.state == 'normal' and instance.text in self.feat_list:
                self.feat_list.remove(instance.text)
        else:
            self.feat_value = instance.text
            self.feat_popup.dismiss()
        self.ch_btn.disabled = False

    def close_feat_popup(self, instance):
        str = ','
        self.feat_value = str.join(self.feat_list)
        self.feat_popup.dismiss()

    def open_channel_popup(self):

        # create the popup
        popup_width = min(0.95 * Window.width, dp(500))
        popup_height = min(0.95 * Window.width, dp(600))
        if len(self.ch_options)*dp(55)+dp(45)+dp(55) < popup_height:
            popup_height = (len(self.ch_options))*dp(55)+dp(45)+dp(120)

        self.ch_popup = SettMultiOptionsMetricPopup()
        self.ch_popup.title = 'Select the channels to compute'
        self.ch_popup.width = popup_width
        self.ch_popup.height = popup_height
        
        # add all the options
        for option in self.ch_options:
            btn = ToggleButton(text=option[1],state='normal',font_size = dp(25),size_hint_y = None,height=dp(55))
            btn.ch_tuple = option
            btn.bind(on_release=self._set_ch_option)
            self.ch_popup.ad_bl.add_widget(btn)

        # finally, add a cancel button to return on the previous panel
        self.ch_popup.done_btn.bind(on_release=self.close_ch_popup)

        # and open the popup !
        self.ch_list = []
        self.ch_list_nr = []
        self.ch_popup.open()

    def _set_ch_option(self, instance):
        if instance.state == 'down':
            self.ch_list.append(instance.text)
            self.ch_list_nr.append(instance.ch_tuple[0])
        elif instance.state == 'normal' and instance.text in self.ch_list:
            self.ch_list.remove(instance.text)
            self.ch_list_nr.remove(instance.ch_tuple[0])

    def close_ch_popup(self, instance):
        str = ','
        self.ch_value = str.join(self.ch_list)
        self.ch_popup.dismiss()

    def enable_metric(self):

        if self.check.active:
            self.method_btn.disabled = False
        else:
            self.ch_btn.disabled = True
            self.feat_btn.disabled = True
            self.method_btn.disabled = True
