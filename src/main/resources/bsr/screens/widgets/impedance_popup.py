from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
Builder.load_file('screens/widgets/impedance_popup.kv')


from pylsl import resolve_byprop,StreamInlet
import os
import time

class ImpedancePopup(Popup):
    
    channel_bl = ObjectProperty()

    def __init__(self,id_sess_name,bsr_cfg,eeg_cfg, **kwargs):
        super(ImpedancePopup,self).__init__(**kwargs)
        self.channel_vect_2Vis = []
        self.chann_lab_2Vis = []
        self.bsr_cfg = bsr_cfg
        self.eeg_cfg = eeg_cfg

        ''' Acquisition Settings'''
        self.id_sess_name = id_sess_name
        
        self.num_eeg_chann = eeg_cfg.nr_chann
        for ch in eeg_cfg.ch2visualize:
            self.channel_vect_2Vis.append(ch[0])
            self.chann_lab_2Vis.append(ch[1])

        lab_bl = BoxLayout()
        lab_bl.add_widget(Label(text='GND',size_hint_x=0.5,font_size = '25dp'))
        lab_bl.add_widget(Label(text='0',size_hint_x=0.5,font_size = '25dp'))
        self.channel_bl.add_widget(lab_bl)

        lab_bl = BoxLayout()
        lab_bl.add_widget(Label(text='REF',size_hint_x=0.5,font_size = '25dp'))
        lab_bl.add_widget(Label(text='0',size_hint_x=0.5,font_size = '25dp'))
        self.channel_bl.add_widget(lab_bl)

        for chann in self.chann_lab_2Vis:
            lab_bl = BoxLayout()
            lab_bl.add_widget(Label(text=chann,size_hint_x=0.5,font_size = '25dp'))
            lab_bl.add_widget(Label(text='0',size_hint_x=0.5,font_size = '25dp'))
            self.channel_bl.add_widget(lab_bl)

        self.founded_imp = False

        if not bsr_cfg.debug:
            self.upd_evt = Clock.schedule_interval(self.update_impedance_label,0.5)
    
    def update_impedance_label(self,dt):

        if self.founded_imp:
            sample_imp, timestamp = self.inlet_imp.pull_chunk(timeout=0.0)
            actual_block_size = sample_imp.__len__()
            if sample_imp:
                sample_imp = sample_imp[-1]
                
                for ndx,child in enumerate(self.channel_bl.children):
                    if int(sample_imp[ndx]) == 3276:
                        self.channel_bl.children[-ndx-1].children[0].text = 'Open'
                    else:    
                        self.channel_bl.children[-ndx-1].children[0].text = str(int(sample_imp[ndx]))

        else:
            ''' Looking for the inlet'''
            if self.bsr_cfg.eeg_device == 'liveAmp' or self.bsr_cfg.eeg_device == 'touch':
                self.imp_streams = resolve_byprop('name', '{}_Impedance'.format(self.eeg_cfg.serial), timeout=0.0)

            if self.imp_streams.__len__() != 0:
                self.inlet_imp = StreamInlet(self.imp_streams[0])
                self.founded_imp = True

    def save_impedances(self):

        imp_save_dir = os.path.join('Data', self.id_sess_name, 'Impedances')
        if not os.path.exists(imp_save_dir):
            os.mkdir(imp_save_dir)

        filename_imp = os.path.join(imp_save_dir, '{}{}{}{}'.format(self.id_sess_name, '_imp_',
                                                                    time.strftime("%d%b%Y_%H_%M_%S",
                                                                                time.localtime()), '.txt'))
        lab = []
        val = []
        rev_bl = self.channel_bl.children[::-1]
        for child in rev_bl:
            lab.append(child.children[1].text)
            val.append(child.children[0].text)
        imp2save = list(zip(lab,val))

        self.file2save_imp = open(filename_imp, 'w')
        for el in imp2save:
            self.file2save_imp.write('{} {} \t\n'.format(el[0],el[1]))
        self.file2save_imp.close()

    def on_dismiss(self):
        if not self.bsr_cfg.debug:
            if self.upd_evt:
                self.upd_evt.cancel()
