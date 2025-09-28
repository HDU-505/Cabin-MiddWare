from kivy.config import Config
Config.set('graphics','width',950)
Config.set('graphics','borderless','true')
Config.set('kivy', 'exit_on_escape', '0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
Window.clearcolor = (1, 1, 1, 1)

from kivy.metrics import dp
from kivy.properties import ObjectProperty,StringProperty,BooleanProperty,NumericProperty,ListProperty

from json.encoder import JSONEncoder
import json
import pathlib
import xml.etree.ElementTree as et
import dicttoxml
from xml.dom.minidom import parseString
import re

import os
images_folder = 'images'

from screens.widgets.adaptable_boxlayout import AdaptableBoxLayout
from screens.widgets.sett_boolean import SettBoolean
from screens.widgets.sett_string import SettString
from screens.widgets.sett_options import SettOptions
from screens.widgets.sett_multioptions import SettMultiOptions
from screens.widgets.sett_spacer import SettSpacer

from kivy.lang import Builder
Builder.load_file('screens/widgets/sett_title.kv')
Builder.load_file('screens/widgets/sett_button.kv')

def string2bool(string):
    if string == 'True':
        return True
    else:
        return False

class ChanNrTextInput(TextInput):
    
    pat = re.compile('[0-9]')
    
    def __init__(self,**kwargs):
        super(ChanNrTextInput,self).__init__(**kwargs)
        self.write_tab = False
        self.font_size = '20dp'
    
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if pat.match(substring):
            s = substring
        else:
            s = ''
        
        return super(ChanNrTextInput, self).insert_text(s, from_undo=from_undo)

class ChannelRow(GridLayout):

    row_height = 35

    def __init__(self,**kwargs):
        super(ChannelRow,self).__init__(**kwargs)
        self.size_hint=(1, None)
        self.height=self.row_height
        self.cols = 7
        self.rows = 1
        self.padding = "5dp"
        self.spacing = "5dp"
        self.build_row()

    def build_row(self):
        
        self.ch_name = TextInput(font_size="15dp",multiline=False,size_hint_y=None,height=self.row_height,halign='right')
        self.add_widget(self.ch_name)
        self.ch_nr = BoxLayout(size_hint_y=None,height=self.row_height)
        self.ch_nr.add_widget(BoxLayout())
        self.ch_nr_txt = ChanNrTextInput(font_size="15dp",multiline=False,halign='right')
        self.ch_nr.add_widget(self.ch_nr_txt)
        self.add_widget(self.ch_nr)
        self.ch_type = Button(size_hint_y=None,height=self.row_height,text='EEG',color = [1,1,1,1],
        font_size = "25dp",background_normal='',background_down='',background_disabled_normal='',background_disabled_down='',
        background_color= [0,0,0,0],pos=self.pos)
        self.add_widget(self.ch_type)
        self.ch_vis = CheckBox(size_hint_y=None,height=self.row_height,allow_no_selection=True)
        self.add_widget(self.ch_vis)
        self.ch_comp = CheckBox(size_hint_y=None,height=self.row_height,allow_no_selection=True)
        self.add_widget(self.ch_comp)
        self.ch_eog = CheckBox(size_hint_y=None,height=self.row_height,allow_no_selection=True)
        self.add_widget(self.ch_eog)
        self.ch_rem = CheckBox(size_hint_y=None,height=self.row_height,allow_no_selection=True)
        self.add_widget(self.ch_rem)

class PresetPopup(Popup):
    pre_bl = ObjectProperty()
    load_btn = ObjectProperty()
    save_btn = ObjectProperty()
    add_btn = ObjectProperty()
    rem_btn = ObjectProperty()

class PresetFilechooser(FloatLayout):
    
    select_file = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(PresetFilechooser, self).__init__(**kwargs)
        self.background = "images/blu_back.png"

class ChOpt(SettMultiOptions):

    value = StringProperty('')

    def add_ch(self,instance):
        self.popup.pre_bl.add_widget(ChannelRow())
        self.popup.pre_bl.add_widget(SettSpacer())

    def rem_ch(self,instance):
        ch2rem = 0
        for ch in self.popup.pre_bl.children:
            if ch.height > 5:
                if ch.ch_rem.active:
                    ch2rem += 1            
        while ch2rem > 0:
            for ndx,ch in enumerate(self.popup.pre_bl.children):
                if ch.height > 5:
                    if ch.ch_rem.active:
                        self.popup.pre_bl.remove_widget(ch)
                        self.popup.pre_bl.remove_widget(self.popup.pre_bl.children[ndx-1])
            ch2rem = 0
            for ch in self.popup.pre_bl.children:
                if ch.height > 5:
                    if ch.ch_rem.active:
                        ch2rem += 1        
        
    def open_save_preset_popup(self,instance):
        # create popup layout
        content = BoxLayout(orientation='vertical', spacing=5)
        self.popup.popup_save = Popup(title='Type the preset filename',title_size='23dp',separator_color = [float(233)/255, float(147)/255, float(34)/255,1],
            content=content, size_hint=(.5, .25),
            background = os.path.join(images_folder,'blu_back.png'))

        self.popup.textinput = textinput = TextInput(text='',
            font_size=20, multiline=False, size_hint_y=.55, height=50,
            hint_text='NumberOfChannel_Ch_device_protocol')
        
        self.popup.textinput = textinput
        content.add_widget(textinput)

        btnlayout = BoxLayout(size_hint_y=.45)#, height=50, spacing=5)
        btn = Button(text='Ok',font_size = '25')
        btn.bind(on_release=self.save_preset)
        btnlayout.add_widget(btn)
        btn = Button(text='Cancel',font_size = "25dp")
        btn.bind(on_release=self.popup.popup_save.dismiss)
        btnlayout.add_widget(btn)
        content.add_widget(btnlayout)

        self.popup.popup_save.open()
    
    def save_preset(self,instance):
        ch_panel = {}
        channels = self.popup.pre_bl.children[::-1]
        for ndx,ch in enumerate(channels):
            if ch.height > 5:
                ch_panel['{}'.format(ch.ch_name.text)] = {'nr':ch.ch_nr_txt.text,'type':ch.ch_type.text,'toVisualize':ch.ch_vis.active,
                'toCompute':ch.ch_comp.active,'eog':ch.ch_eog.active}

        jsonString = JSONEncoder().encode({'channels':ch_panel})
        
        xml_str = dicttoxml.dicttoxml(json.loads(jsonString),attr_type=False,root = True,custom_root='root',item_func=lambda parent: 'label')
        
        dom = parseString(xml_str)
        
        with open(os.path.join('Preset','{}.xml'.format(self.popup.textinput.text)),'w') as out:
            out.write(dom.toprettyxml())

        self.popup.popup_save.dismiss()

    def open_load_preset_popup(self,instance):

        content = PresetFilechooser(select_file=self.select_file)

        self.popup.popup_load = Popup(title='Select a Preset File', content=content,
                            separator_color=[float(233) / 255, float(147) / 255, float(34) / 255, 1],
                            background="images/blu_back.png", title_size="30dp", size_hint=(0.8, 0.6))

        self.popup.popup_load.open()

    def select_file(self, path, filename):

        title = self.popup.popup_load.title
        fname_path = pathlib.PurePath(path) / pathlib.PurePath(filename[0]).name
        self.open_preset(fname_path)
        self.popup.popup_load.dismiss()

    def open_preset(self,filename):

        for child in [child for child in self.popup.pre_bl.children]:
            self.popup.pre_bl.remove_widget(child)      

        preset_xml = et.parse(filename)
        chan_xml = preset_xml.find('channels')
        for ch in chan_xml:
            channel = ChannelRow()
            channel.ch_name.text = ch.tag
            channel.ch_nr_txt.text = ch.find('nr').text
            channel.ch_type.text = ch.find('type').text
            channel.ch_vis.active = string2bool(ch.find('toVisualize').text)
            channel.ch_comp.active = string2bool(ch.find('toCompute').text)
            channel.ch_eog.active = string2bool(ch.find('eog').text)
            self.popup.pre_bl.add_widget(channel)
            self.popup.pre_bl.add_widget(SettSpacer())

class LAChOpt(ChOpt):
    
    def create_popup(self):
        self.popup = PresetPopup()
        this_app = App.get_running_app()
        home = this_app.root

        for ch,prop in home.cfg_sm.liveamp.ch_prop.items():
            channel = ChannelRow()
            channel.ch_name.text = ch
            channel.ch_nr_txt.text = prop['nr']
            channel.ch_type.text = prop['type']
            channel.ch_vis.active = prop['toVisualize'] 
            channel.ch_comp.active = prop['toCompute'] 
            channel.ch_eog.active = prop['eog'] 
            self.popup.pre_bl.add_widget(channel)
            self.popup.pre_bl.add_widget(SettSpacer())

        self.popup.load_btn.bind(on_press=self.open_load_preset_popup)
        self.popup.save_btn.bind(on_press=self.open_save_preset_popup)
        self.popup.add_btn.bind(on_press=self.add_ch)
        self.popup.rem_btn.bind(on_press=self.rem_ch)
        self.popup.close_btn.bind(on_press=self.close_popup)
        self.popup.open()

    def close_popup(self,instance):

        this_app = App.get_running_app()
        home = this_app.root
        home.cfg_sm.liveamp.ch_prop = {}
        self.value = ''
        ch_panel = {}

        channels = self.popup.pre_bl.children[::-1]
        for ndx,ch in enumerate(channels):
            if ch.height > 5:
                self.value = self.value + ch.ch_name.text + ','

                home.cfg_sm.liveamp.ch_prop['{}'.format(ch.ch_name.text)] = {'nr':ch.ch_nr_txt.text,'type':ch.ch_type.text,'toVisualize':ch.ch_vis.active,
                'toCompute':ch.ch_comp.active,'eog':ch.ch_eog.active}
        
        self.value = self.value[:-1]

        self.popup.dismiss()

class THChOpt(ChOpt):
    
    def create_popup(self):
        self.popup = PresetPopup()
        this_app = App.get_running_app()
        home = this_app.root

        for ch,prop in home.cfg_sm.touch.ch_prop.items():
            channel = ChannelRow()
            channel.ch_name.text = ch
            channel.ch_nr_txt.text = prop['nr']
            channel.ch_type.text = prop['type']
            channel.ch_vis.active = prop['toVisualize'] 
            channel.ch_comp.active = prop['toCompute'] 
            channel.ch_eog.active = prop['eog'] 
            self.popup.pre_bl.add_widget(channel)
            self.popup.pre_bl.add_widget(SettSpacer())

        self.popup.load_btn.bind(on_press=self.open_load_preset_popup)
        self.popup.save_btn.bind(on_press=self.open_save_preset_popup)
        self.popup.add_btn.bind(on_press=self.add_ch)
        self.popup.rem_btn.bind(on_press=self.rem_ch)
        self.popup.close_btn.bind(on_press=self.close_popup)
        self.popup.open()

    def close_popup(self,instance):

        this_app = App.get_running_app()
        home = this_app.root
        home.cfg_sm.touch.ch_prop = {}
        self.value = ''
        ch_panel = {}

        channels = self.popup.pre_bl.children[::-1]
        for ndx,ch in enumerate(channels):
            if ch.height > 5:
                self.value = self.value + ch.ch_name.text + ','

                home.cfg_sm.touch.ch_prop['{}'.format(ch.ch_name.text)] = {'nr':ch.ch_nr_txt.text,'type':ch.ch_type.text,'toVisualize':ch.ch_vis.active,
                'toCompute':ch.ch_comp.active,'eog':ch.ch_eog.active}
        
        self.value = self.value[:-1]

        self.popup.dismiss()

class MuChOpt(ChOpt):
    
    def create_popup(self):
        self.popup = PresetPopup()
        this_app = App.get_running_app()
        home = this_app.root

        for ch,prop in home.cfg_sm.muse.ch_prop.items():
            channel = ChannelRow()
            channel.ch_name.text = ch
            channel.ch_nr_txt.text = prop['nr']
            channel.ch_type.text = prop['type']
            channel.ch_vis.active = prop['toVisualize'] 
            channel.ch_comp.active = prop['toCompute'] 
            channel.ch_eog.active = prop['eog'] 
            self.popup.pre_bl.add_widget(channel)
            self.popup.pre_bl.add_widget(SettSpacer())

        self.popup.load_btn.bind(on_press=self.open_load_preset_popup)
        self.popup.save_btn.bind(on_press=self.open_save_preset_popup)
        self.popup.add_btn.bind(on_press=self.add_ch)
        self.popup.rem_btn.bind(on_press=self.rem_ch)
        self.popup.close_btn.bind(on_press=self.close_popup)
        self.popup.open()

    def close_popup(self,instance):

        this_app = App.get_running_app()
        home = this_app.root
        home.cfg_sm.muse.ch_prop = {}
        self.value = ''
        ch_panel = {}
        
        channels = self.popup.pre_bl.children[::-1]
        for ndx,ch in enumerate(channels):
            if ch.height > 5:
                self.value = self.value + ch.ch_name.text + ','

                home.cfg_sm.muse.ch_prop['{}'.format(ch.ch_name.text)] = {'nr':ch.ch_nr_txt.text,'type':ch.ch_type.text,'toVisualize':ch.ch_vis.active,
                'toCompute':ch.ch_comp.active,'eog':ch.ch_eog.active}
        
        self.value = self.value[:-1]

        self.popup.dismiss()

class FKChOpt(ChOpt):
    
    def create_popup(self):
        self.popup = PresetPopup()
        this_app = App.get_running_app()
        home = this_app.root

        for ch,prop in home.cfg_sm.fake.ch_prop.items():
            channel = ChannelRow()
            channel.ch_name.text = ch
            channel.ch_nr_txt.text = prop['nr']
            channel.ch_type.text = prop['type']
            channel.ch_vis.active = prop['toVisualize'] 
            channel.ch_comp.active = prop['toCompute'] 
            channel.ch_eog.active = prop['eog'] 
            self.popup.pre_bl.add_widget(channel)
            self.popup.pre_bl.add_widget(SettSpacer())

        self.popup.load_btn.bind(on_press=self.open_load_preset_popup)
        self.popup.save_btn.bind(on_press=self.open_save_preset_popup)
        self.popup.add_btn.bind(on_press=self.add_ch)
        self.popup.rem_btn.bind(on_press=self.rem_ch)
        self.popup.close_btn.bind(on_press=self.close_popup)
        self.popup.open()

    def close_popup(self,instance):

        this_app = App.get_running_app()
        home = this_app.root
        home.cfg_sm.fake.ch_prop = {}
        self.value = ''
        ch_panel = {}

        channels = self.popup.pre_bl.children[::-1]
        for ndx,ch in enumerate(channels):
            if ch.height > 5:
                self.value = self.value + ch.ch_name.text + ','

                home.cfg_sm.fake.ch_prop['{}'.format(ch.ch_name.text)] = {'nr':ch.ch_nr_txt.text,'type':ch.ch_type.text,'toVisualize':ch.ch_vis.active,
                'toCompute':ch.ch_comp.active,'eog':ch.ch_eog.active}
        
        self.value = self.value[:-1]

        self.popup.dismiss()

class General(Screen):

    debug = ObjectProperty()
    user = ObjectProperty()
    fullscreen = ObjectProperty()
    device = ObjectProperty()
    keyboard = ObjectProperty()
    eeg = ObjectProperty()
    eeg_dev = ObjectProperty()
    gsr = ObjectProperty()
    gsr_dev = ObjectProperty()
    ppg = ObjectProperty()
    ppg_dev = ObjectProperty()

    def __init__(self,**kwargs):
        super(General,self).__init__(**kwargs)

class LiveAmp(Screen):

    la_ser_opt = ObjectProperty()
    la_fs_opt = ObjectProperty()
    la_bs_opt = ObjectProperty()
    la_ch_opt = ObjectProperty()
    ch_prop = {}

    def __init__(self,**kwargs):
        super(LiveAmp,self).__init__(**kwargs)

class Touch(Screen):

    th_ser_opt = ObjectProperty()
    th_fs_opt = ObjectProperty()
    th_bs_opt = ObjectProperty()
    th_ch_opt = ObjectProperty()
    ch_prop = {}

    def __init__(self,**kwargs):
        super(Touch,self).__init__(**kwargs)

class Muse(Screen):
    
    mu_ser_opt = ObjectProperty()
    mu_ch_opt = ObjectProperty()
    ch_prop = {}

    def __init__(self,**kwargs):
        super(Muse,self).__init__(**kwargs)

class Shimmer(Screen):

    sh_ser_opt = ObjectProperty()
    # sh_com_opt = ObjectProperty()
    sh_fs_opt = ObjectProperty()
    # ppg = ObjectProperty()

    def __init__(self,**kwargs):
        super(Shimmer,self).__init__(**kwargs)

class Empatica(Screen):
    em_ser_opt = ObjectProperty()
    gui = ObjectProperty()

    def __init__(self,**kwargs):
        super(Empatica,self).__init__(**kwargs)

class Fake(Screen):
    fk_eeg = ObjectProperty()
    fk_ch_opt = ObjectProperty()
    fk_gsr = ObjectProperty()
    fk_ppg = ObjectProperty()
    ch_prop = {}

    def __init__(self,**kwargs):
        super(Fake,self).__init__(**kwargs)

class CFGSM(ScreenManager):

    general = ObjectProperty()
    liveamp = ObjectProperty()
    touch = ObjectProperty()
    muse = ObjectProperty()
    shimmer = ObjectProperty()
    empatica = ObjectProperty()
    fake = ObjectProperty()

    def __init__(self, **kwargs):
        super(CFGSM, self).__init__(**kwargs)
        self.general = General()
        self.add_widget(self.general)
        self.current = 'general'
        self.liveamp = LiveAmp(name = 'liveamp')
        self.add_widget(self.liveamp)
        self.touch = Touch(name = 'touch')
        self.add_widget(self.touch)
        self.muse = Muse(name = 'muse')
        self.add_widget(self.muse)
        self.shimmer = Shimmer(name = 'shimmer')
        self.add_widget(self.shimmer)
        self.empatica = Empatica(name = 'empatica')
        self.add_widget(self.empatica)
        # self.fake = Fake(name = 'fake')
        # self.add_widget(self.fake)

class Home(BoxLayout):

    cfg_sm = ObjectProperty()

    def __init__(self, **kwargs):
        super(Home, self).__init__(**kwargs)

        self.cfg_sm = CFGSM()
        self.add_widget(self.cfg_sm)

    def go_to_general(self):
        self.cfg_sm.current = 'general'

    def go_to_liveamp(self):
        self.cfg_sm.current = 'liveamp'

    def go_to_touch(self):
        self.cfg_sm.current = 'touch'

    def go_to_muse(self):
        self.cfg_sm.current = 'muse'

    def go_to_shimmer(self):
        self.cfg_sm.current = 'shimmer'

    def go_to_empatica(self):
        self.cfg_sm.current = 'empatica'

    # def go_to_fake(self):
    #     self.cfg_sm.current = 'fake'
    
    def write_config_xml(self):

        general_panel = {'debug':self.cfg_sm.general.debug.check.active, 'user':self.cfg_sm.general.user.value,
        'fullscreen':self.cfg_sm.general.fullscreen.check.active,'keyboardMode':self.cfg_sm.general.keyboard.value,
        'device':self.cfg_sm.general.device.value,
        'EEG':self.cfg_sm.general.eeg.check.active,'EEG_sensor':self.cfg_sm.general.eeg_dev.value,
        'GSR':self.cfg_sm.general.gsr.check.active,'GSR_sensor':self.cfg_sm.general.gsr_dev.value,
        'PPG':self.cfg_sm.general.ppg.check.active,'PPG_sensor':self.cfg_sm.general.ppg_dev.value}
    
        jsonString = JSONEncoder().encode({'general':general_panel})
        xml_str = dicttoxml.dicttoxml(json.loads(jsonString),attr_type=False,root = True,custom_root='start_config')
        dom = parseString(xml_str)    
        with open(os.path.join('start_config.xml'), 'w') as out:
            out.write(dom.toprettyxml())
        
        # if self.cfg_sm.general.debug.check.active:
        #     self.write_fake_config()
        # else:
        self.write_fake_config()
        if self.cfg_sm.general.eeg.check.active:
            if self.cfg_sm.general.eeg_dev.value == 'liveAmp':
                self.write_liveamp_config()
            elif self.cfg_sm.general.eeg_dev.value == 'touch':
                self.write_touch_config()
        self.write_muse_config()
        self.write_shimmer_config()
        self.write_empatica_config()

        # if self.cfg_sm.general.eeg.check.active:
        #     if self.cfg_sm.general.eeg_dev.value == 'liveAmp':
        #         self.write_liveamp_config()
        #     elif self.cfg_sm.general.eeg_dev.value == 'muse':
        #         self.write_muse_config()

        # if self.cfg_sm.general.gsr.check.active:
        #     if self.cfg_sm.general.gsr_dev.value == 'shimmer':
        #         self.write_shimmer_config()
        #     elif self.cfg_sm.general.gsr_dev.value == 'empatica':
        #         self.write_empatica_config()

        App.get_running_app().stop()
    
    def write_liveamp_config(self):
                
        settings_panel = {'amplifierFamily':0,'deviceNumber':self.cfg_sm.liveamp.la_ser_opt.value,'channelcount':self.cfg_sm.liveamp.la_ch_opt.value.split(',').__len__(),
        'samplingRate':self.cfg_sm.liveamp.la_fs_opt.value,'chunksize':self.cfg_sm.liveamp.la_bs_opt.value}

        ch_panel = self.cfg_sm.liveamp.ch_prop
        
        jsonString = JSONEncoder().encode({'settings':settings_panel,'channels':ch_panel})
        
        xml_str = dicttoxml.dicttoxml(json.loads(jsonString),attr_type=False,root = True,custom_root='root',item_func=lambda parent: 'label')
        
        dom = parseString(xml_str)
        
        with open(os.path.join('Apps','EegAmpApp','config.cfg'), 'w') as out:
            out.write(dom.toprettyxml())

    def write_touch_config(self):
        settings_panel = {'amplifierFamily':2,'deviceNumber':self.cfg_sm.touch.th_ser_opt.value,'channelcount':self.cfg_sm.touch.th_ch_opt.value.split(',').__len__(),
        'samplingRate':self.cfg_sm.touch.th_fs_opt.value,'chunksize':self.cfg_sm.touch.th_bs_opt.value}

        ch_panel = self.cfg_sm.touch.ch_prop
        
        jsonString = JSONEncoder().encode({'settings':settings_panel,'channels':ch_panel})
        
        xml_str = dicttoxml.dicttoxml(json.loads(jsonString),attr_type=False,root = True,custom_root='root',item_func=lambda parent: 'label')
        
        dom = parseString(xml_str)
        
        with open(os.path.join('Apps','EegAmpApp','config.cfg'), 'w') as out:
            out.write(dom.toprettyxml())

    def write_muse_config(self):
        
        serial_dict = {'4B04':'4B04 (00:55:da:b7:4b:04)','70F8':'70F8 (00:55:da:b7:70:f8)','7673':'7673 (00:55:da:b7:76:73)','2B01':'2B01 (00:55:da:bb:2b:01)'}
        # serial_dict[self.cfg_sm.muse.mu_ser_opt.value]
        settings_panel = {'deviceNumber':self.cfg_sm.muse.mu_ser_opt.value,'channelcount':self.cfg_sm.muse.mu_ch_opt.value.split(',').__len__(),
        'samplingRate':'256','chunksize':'12'}

        if self.cfg_sm.general.ppg.check.active and self.cfg_sm.general.ppg_dev.value == 'muse':
            settings_panel['ppg'] = True
        else: 
            settings_panel['ppg'] = False

        settings_panel['fs_ppg'] = 64
        settings_panel['bs_ppg'] = 8

        ch_panel = self.cfg_sm.muse.ch_prop
        
        jsonString = JSONEncoder().encode({'settings':settings_panel,'channels':ch_panel})
        
        xml_str = dicttoxml.dicttoxml(json.loads(jsonString),attr_type=False,root = True,custom_root='root',item_func=lambda parent: 'label')
        
        dom = parseString(xml_str)
        
        with open(os.path.join('Apps','MuseApp','config.cfg'), 'w') as out:
            out.write(dom.toprettyxml())

    def write_shimmer_config(self):

        general_panel = {'serial':self.cfg_sm.shimmer.sh_ser_opt.value,#'COM':'com{}'.format(self.cfg_sm.shimmer.sh_com_opt.value),
        'fs_gsr':self.cfg_sm.shimmer.sh_fs_opt.value}

        if float(self.cfg_sm.shimmer.sh_fs_opt.value) == 51.2:
            bs = 5  
        elif float(self.cfg_sm.shimmer.sh_fs_opt.value) == 64:
            bs = 8
        elif float(self.cfg_sm.shimmer.sh_fs_opt.value) == 102.4:
            bs = 10
        elif float(self.cfg_sm.shimmer.sh_fs_opt.value) == 128:
            bs = 16

        general_panel['bs_gsr'] = bs

        if self.cfg_sm.general.ppg.check.active and self.cfg_sm.general.ppg_dev.value == 'shimmer':
            general_panel['ppg'] = True 
        else: 
            general_panel['ppg'] = False


        # general_panel['ppg'] = self.cfg_sm.shimmer.ppg.check.active
        general_panel['fs_ppg'] = self.cfg_sm.shimmer.sh_fs_opt.value
        general_panel['bs_ppg'] = bs

        jsonString = JSONEncoder().encode({'general':general_panel})
        
        xml_str = dicttoxml.dicttoxml(json.loads(jsonString),attr_type=False,root = True,custom_root='root')
        
        dom = parseString(xml_str)
        
        with open(os.path.join('Apps','ShimmerApp','config.cfg'), 'w') as out:
            out.write(dom.toprettyxml())
        
    def write_empatica_config(self):

        general_panel = {'serial':self.cfg_sm.empatica.em_ser_opt.value,'gui':self.cfg_sm.empatica.gui.check.active,'fs_gsr':4,'bs_gsr':1}

        if self.cfg_sm.general.ppg.check.active and self.cfg_sm.general.ppg_dev.value == 'empatica':
            general_panel['ppg'] = True 
        else: 
            general_panel['ppg'] = False

        # general_panel['ppg'] = self.cfg_sm.shimmer.ppg.check.active
        general_panel['fs_ppg'] = 64
        general_panel['bs_ppg'] = 8

        jsonString = JSONEncoder().encode({'general':general_panel})
        
        xml_str = dicttoxml.dicttoxml(json.loads(jsonString),attr_type=False,root = True,custom_root='root')
        
        dom = parseString(xml_str)
        
        with open(os.path.join('Apps','EmpaticaApp','config.cfg'), 'w') as out:
            out.write(dom.toprettyxml())

    def write_fake_config(self):
        settings_panel = {'eeg':self.cfg_sm.general.eeg.check.active,'eeg_dev':self.cfg_sm.general.eeg_dev.value,
        'gsr':self.cfg_sm.general.gsr.check.active,'ppg':self.cfg_sm.general.ppg.check.active}

        if self.cfg_sm.general.eeg_dev.value == 'liveAmp':
            settings_panel['channelcount'] =self.cfg_sm.liveamp.la_ch_opt.value.split(',').__len__()
        elif self.cfg_sm.general.eeg_dev.value == 'touch':
            settings_panel['channelcount'] =self.cfg_sm.touch.th_ch_opt.value.split(',').__len__()
        elif self.cfg_sm.general.eeg_dev.value == 'muse':
            settings_panel['channelcount'] =self.cfg_sm.muse.mu_ch_opt.value.split(',').__len__()
        
        jsonString = JSONEncoder().encode({'settings':settings_panel})        
        
        xml_str = dicttoxml.dicttoxml(json.loads(jsonString),attr_type=False,root = True,custom_root='root',item_func=lambda parent: 'label')
        
        dom = parseString(xml_str)
        
        with open(os.path.join('Apps','FakeApp','config.cfg'), 'w') as out:
            out.write(dom.toprettyxml())

    def read_config_xml(self):

        if os.path.isfile(os.path.join('start_config.xml')):
            tree = et.parse(os.path.join('start_config.xml'))
            gen = tree.find('general')

            self.cfg_sm.general.debug.check.active  = string2bool(gen.find('debug').text)
            self.cfg_sm.general.user.value = gen.find('user').text
            self.cfg_sm.general.fullscreen.check.active = string2bool(gen.find('fullscreen').text)
            self.cfg_sm.general.keyboard.value = gen.find('keyboardMode').text
            self.cfg_sm.general.device.value = gen.find('device').text
            self.cfg_sm.general.eeg.check.active = string2bool(gen.find('EEG').text)
            self.cfg_sm.general.eeg_dev.value = gen.find('EEG_sensor').text
            self.cfg_sm.general.gsr.check.active = string2bool(gen.find('GSR').text)
            self.cfg_sm.general.gsr_dev.value = gen.find('GSR_sensor').text
            self.cfg_sm.general.ppg.check.active = string2bool(gen.find('PPG').text)
            self.cfg_sm.general.ppg_dev.value = gen.find('PPG_sensor').text
         
            # if not self.cfg_sm.general.debug.check.active:
            #     self.cfg_sm.general.eeg.check.active = string2bool(gen.find('EEG').text)
            #     if not string2bool(gen.find('EEG').text):
            #         self.cfg_sm.general.eeg_dev.cfg_button.disabled = True
            #     # else:
            #         # if gen.find('EEG_sensor').text == 'liveAmp':
            #         #     self.cfg_menu.la_button.disabled = False
            #         # elif gen.find('EEG_sensor').text == 'muse':
            #         #     self.cfg_menu.muse_button.disabled = False
            #     self.cfg_sm.general.eeg_dev.value = gen.find('EEG_sensor').text
                

            #     self.cfg_sm.general.gsr.check.active = string2bool(gen.find('GSR').text)
            #     if not string2bool(gen.find('GSR').text):
            #         self.cfg_sm.general.gsr_dev.cfg_button.disabled = True
            #     # else:
            #     #     if gen.find('GSR_sensor').text == 'shimmer':
            #     #         self.cfg_menu.sh_button.disabled = False
            #     #     elif gen.find('GSR_sensor').text == 'empatica':
            #     #         self.cfg_menu.emp_button.disabled = False
            #     self.cfg_sm.general.gsr_dev.value = gen.find('GSR_sensor').text

            #     self.cfg_sm.general.ppg.check.active = string2bool(gen.find('PPG').text)
            #     self.cfg_sm.general.ppg_dev.value = gen.find('PPG_sensor').text
            #     if not string2bool(gen.find('PPG').text):
            #         self.cfg_sm.general.ppg_dev.cfg_button.disabled = True

            # else:
            #     self.cfg_sm.general.eeg.check.disabled = True
            #     self.cfg_sm.general.gsr.check.disabled = True
            #     self.cfg_sm.general.eeg_dev.cfg_button.disabled = True
            #     self.cfg_sm.general.gsr_dev.cfg_button.disabled = True
            #     self.cfg_sm.general.ppg.check.disabled = True
            #     self.cfg_sm.general.ppg_dev.cfg_button.disabled = True
            #     self.cfg_menu.fk_button.disabled = False

            ''' Config.cfg File reading'''
            if os.path.isfile(os.path.join('Apps','EegAmpApp','config.cfg')):
                self.read_liveamp_config()
                self.read_touch_config()
            if os.path.isfile(os.path.join('Apps','MuseApp','config.cfg')):
                self.read_muse_config()

            if os.path.isfile(os.path.join('Apps','ShimmerApp','config.cfg')):
                self.read_shimmer_config()
            if os.path.isfile(os.path.join('Apps','EmpaticaApp','config.cfg')):
                self.read_empatica_config()

            # if os.path.isfile(os.path.join('Apps','FakeApp','config.cfg')):
            #     self.read_fake_config()
    
    def read_liveamp_config(self):
        et_amp = et.parse(os.path.join('Apps','EegAmpApp','config.cfg'))
        sett_amp = et_amp.find('settings')
        chan_amp = et_amp.find('channels')
        if int(sett_amp.find('amplifierFamily').text) == 0:
            self.cfg_sm.liveamp.la_ser_opt.value = sett_amp.find('deviceNumber').text
            self.cfg_sm.liveamp.la_fs_opt.value = sett_amp.find('samplingRate').text
        else:
            self.cfg_sm.liveamp.la_ser_opt.value = "055602-0332"
            self.cfg_sm.liveamp.la_fs_opt.value = "250" 

        self.cfg_sm.liveamp.la_bs_opt.value = sett_amp.find('chunksize').text

        for ch in chan_amp:
            self.cfg_sm.liveamp.la_ch_opt.value = self.cfg_sm.liveamp.la_ch_opt.value + ch.tag + ','

            self.cfg_sm.liveamp.ch_prop['{}'.format(ch.tag)] = {'nr':ch.find('nr').text,'type':ch.find('type').text,'toVisualize':string2bool(ch.find('toVisualize').text),
            'toCompute':string2bool(ch.find('toCompute').text),'eog':string2bool(ch.find('eog').text)}

        self.cfg_sm.liveamp.la_ch_opt.value = self.cfg_sm.liveamp.la_ch_opt.value[:-1]

    def read_touch_config(self):
        et_amp = et.parse(os.path.join('Apps','EegAmpApp','config.cfg'))
        sett_amp = et_amp.find('settings')
        chan_amp = et_amp.find('channels')

        if int(sett_amp.find('amplifierFamily').text) == 2:    
            self.cfg_sm.touch.th_ser_opt.value = sett_amp.find('deviceNumber').text
            self.cfg_sm.touch.th_fs_opt.value = sett_amp.find('samplingRate').text
        else:
            self.cfg_sm.touch.th_ser_opt.value = "101402-0001"
            self.cfg_sm.touch.th_fs_opt.value = "125"

        self.cfg_sm.touch.th_bs_opt.value = sett_amp.find('chunksize').text

        for ch in chan_amp:
            self.cfg_sm.touch.th_ch_opt.value = self.cfg_sm.touch.th_ch_opt.value + ch.tag + ','

            self.cfg_sm.touch.ch_prop['{}'.format(ch.tag)] = {'nr':ch.find('nr').text,'type':ch.find('type').text,'toVisualize':string2bool(ch.find('toVisualize').text),
            'toCompute':string2bool(ch.find('toCompute').text),'eog':string2bool(ch.find('eog').text)}

        self.cfg_sm.touch.th_ch_opt.value = self.cfg_sm.touch.th_ch_opt.value[:-1]

    def read_muse_config(self):
        
        et_amp = et.parse(os.path.join('Apps','MuseApp','config.cfg'))
        sett_amp = et_amp.find('settings')
        chan_amp = et_amp.find('channels')
        
        self.cfg_sm.muse.mu_ser_opt.value = sett_amp.find('deviceNumber').text

        for ch in chan_amp:
            self.cfg_sm.muse.mu_ch_opt.value = self.cfg_sm.muse.mu_ch_opt.value + ch.tag + ','
            self.cfg_sm.muse.ch_prop['{}'.format(ch.tag)] = {'nr':ch.find('nr').text,'type':ch.find('type').text,'toVisualize':string2bool(ch.find('toVisualize').text),
            'toCompute':string2bool(ch.find('toCompute').text),'eog':string2bool(ch.find('eog').text)}
 
        self.cfg_sm.muse.mu_ch_opt.value = self.cfg_sm.muse.mu_ch_opt.value[:-1]

    def read_shimmer_config(self):
        et_amp = et.parse(os.path.join('Apps','ShimmerApp','config.cfg'))
        gen = et_amp.find('general')

        self.cfg_sm.shimmer.sh_ser_opt.value = gen.find('serial').text
        # self.cfg_sm.shimmer.sh_com_opt.value = re.findall("\d+",gen.find('COM').text)[0]
        self.cfg_sm.shimmer.sh_fs_opt.value = gen.find('fs_gsr').text
        # self.cfg_sm.shimmer.ppg.check.active = string2bool(gen.find('ppg').text)

    def read_empatica_config(self):
        et_amp = et.parse(os.path.join('Apps','EmpaticaApp','config.cfg'))
        gen = et_amp.find('general')

        self.cfg_sm.empatica.em_ser_opt.value = gen.find('serial').text
        self.cfg_sm.empatica.gui.check.active = string2bool(gen.find('gui').text)

    def read_fake_config(self):
        et_amp = et.parse(os.path.join('Apps','FakeApp','config.cfg'))

        sett_amp = et_amp.find('settings')
        chan_amp = et_amp.find('channels')

        self.cfg_sm.fake.fk_eeg.check.active = string2bool(sett_amp.find('eeg').text)
        self.cfg_sm.fake.fk_gsr.check.active = string2bool(sett_amp.find('gsr').text)
        self.cfg_sm.fake.fk_ppg.check.active = string2bool(sett_amp.find('ppg').text)

        for ch in chan_amp:
            self.cfg_sm.fake.fk_ch_opt.value = self.cfg_sm.fake.fk_ch_opt.value + ch.tag + ','
            self.cfg_sm.fake.ch_prop['{}'.format(ch.tag)] = {'nr':ch.find('nr').text,'type':ch.find('type').text,'toVisualize':string2bool(ch.find('toVisualize').text),
            'toCompute':string2bool(ch.find('toCompute').text),'eog':string2bool(ch.find('eog').text)}

        self.cfg_sm.fake.fk_ch_opt.value = self.cfg_sm.fake.fk_ch_opt.value[:-1]        

class CONFIGApp(App):
    
    # h = ObjectProperty()

    def build(self):
        self.title = 'BSR Configuration App'
        h = Home()
        h.read_config_xml()
        inspector.create_inspector(Window,h)
        return h        

if __name__ == "__main__":
    CONFIGApp().run()
