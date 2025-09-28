import os
import os.path
import sys
from json.encoder import JSONEncoder
import xml.etree.ElementTree as et
import dicttoxml
from xml.dom.minidom import parseString
from kivy.uix.floatlayout import FloatLayout
import json

from kivy.app import App
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.core.window import Window

from kivy.properties import ObjectProperty, StringProperty, NumericProperty, ListProperty, Property,BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.lang import Builder

from screens.widgets.scale_label import ScaleLabel
# from widgets.scale_label import ScaleLabel

def string2bool(string):
    if string == 'True':
        return True
    else:
        return False

class General(Screen):

    id_sub = ObjectProperty()
    sess_sub = ObjectProperty()
    prot = ObjectProperty()
    vis_win = ObjectProperty()
    upd_fr = ObjectProperty()
    ws = ObjectProperty()

    def __init__(self,**kwargs):
        super(General,self).__init__(**kwargs)

class Processing(Screen):

    ep = ObjectProperty()
    shift = ObjectProperty()
    ma = ObjectProperty()
    iaf = ObjectProperty()
    filt = ObjectProperty()
    hp = ObjectProperty()
    lp = ObjectProperty()
    filt_eog = ObjectProperty()
    hp_eog = ObjectProperty()
    lp_eog = ObjectProperty()
    en_art = ObjectProperty()
    en_art_th = ObjectProperty()
    art_th = ObjectProperty()
    en_art_diff = ObjectProperty()
    art_diff_min_dist = ObjectProperty()
    proc_method = ObjectProperty()
    blink_method = ObjectProperty()

    def __init__(self,**kwargs):
        super(Processing,self).__init__(**kwargs)

class Metrics(Screen):
    wl = ObjectProperty()
    att = ObjectProperty()
    aw = ObjectProperty()
    ar = ObjectProperty()
    st = ObjectProperty()
    vg = ObjectProperty()

    def __init__(self,eeg_cfg,**kwargs):
        super(Metrics,self).__init__(**kwargs)
        # self.ar.ch_btn.disabled = True

        for ch in eeg_cfg.ch2compute:
            self.wl.ch_options.append(ch)
            self.att.ch_options.append(ch)
            self.aw.ch_options.append(ch)
            self.st.ch_options.append(ch)
            self.vg.ch_options.append(ch)
        self.ar.ch_options.append((-1,'GSR'))
        self.st.ch_options.append((-1,'GSR'))

class SettSM(ScreenManager):
    
    general = ObjectProperty()
    processing = ObjectProperty()
    metrics = ObjectProperty()
    
    def __init__(self,eeg_cfg,**kwargs):
        super(SettSM, self).__init__(**kwargs)
        self.general = General()
        self.add_widget(self.general)
        self.current = 'general'
        self.processing = Processing()
        self.add_widget(self.processing)        
        self.metrics = Metrics(eeg_cfg)
        self.add_widget(self.metrics)

class BSRSettings(Screen):

    set_sm = ObjectProperty()
    bl = ObjectProperty()

    def __init__(self,bsr_cfg,eeg_cfg, **kwargs):
        super(BSRSettings, self).__init__(**kwargs)

        self.use_eeg = bsr_cfg.use_eeg
        self.use_gsr = bsr_cfg.use_gsr
        self.use_ppg = bsr_cfg.use_ppg

        self.set_sm = SettSM(eeg_cfg)
        self.bl.add_widget(self.set_sm)

    def close_settings(self):

        # ok = self.check_gsr_metric()

        # if ok:
        #     ok = self.check_attention_config()
        #     if ok:
        ok = self.check_metrics()
        if ok:
            self.write_settings_xml()
        
        return ok

    def check_metrics(self):
        ok = []
        if self.set_sm.metrics.wl.check.active:
            if self.set_sm.metrics.wl.method_value == '' or self.set_sm.metrics.wl.ch_value == '' or self.set_sm.metrics.wl.feat_value == '':
                self.warning_pop = WarningPopup()
                self.warning_pop.lab_txt = 'Workload metric missing fields.'
                self.warning_pop.open()
                ok.append(0)
            else:
                ok.append(1)

        if self.set_sm.metrics.att.check.active:
            if self.set_sm.metrics.att.method_value == '' or self.set_sm.metrics.att.ch_value == '' or self.set_sm.metrics.att.feat_value == '':
                self.warning_pop = WarningPopup()
                self.warning_pop.lab_txt = 'Attention metric missing fields.'
                self.warning_pop.open()
                ok.append(0)
            else:
                ok.append(1)


        if self.set_sm.metrics.aw.check.active:
            if self.set_sm.metrics.aw.method_value == '' or self.set_sm.metrics.aw.ch_value == '' or self.set_sm.metrics.aw.feat_value == '':
                self.warning_pop = WarningPopup()
                self.warning_pop.lab_txt = 'Approach Withdrawal metric missing fields.'
                self.warning_pop.open()
                ok.append(0)
            else:
                ok.append(1)


        if self.set_sm.metrics.st.check.active:
            if self.set_sm.metrics.st.method_value == '' or self.set_sm.metrics.st.ch_value == '' or self.set_sm.metrics.st.feat_value == '':
                self.warning_pop = WarningPopup()
                self.warning_pop.lab_txt = 'Stress metric missing fields.'
                self.warning_pop.open()
                ok.append(0)
            else:
                ok.append(1)


        if self.set_sm.metrics.vg.check.active:
            if self.set_sm.metrics.vg.method_value == '' or self.set_sm.metrics.vg.ch_value == '' or self.set_sm.metrics.vg.feat_value == '':
                self.warning_pop = WarningPopup()
                self.warning_pop.lab_txt = 'Vigilance metric missing fields.'
                self.warning_pop.open()
                ok.append(0)
            else:
                ok.append(1)

        if self.set_sm.metrics.ar.check.active:
            if self.set_sm.metrics.ar.method_value == '' or self.set_sm.metrics.ar.ch_value == '' or self.set_sm.metrics.ar.feat_value == '':
                self.warning_pop = WarningPopup()
                self.warning_pop.lab_txt = 'Arousal metric missing fields.'
                self.warning_pop.open()
                ok.append(0)
            else:
                ok.append(1)
        
        if len(ok) != 0:
            if sum(ok)/len(ok)  < 1:
                return False
            else:
                return True
        else:
            return True
            
    def check_gsr_metric(self):

        if self.set_sm.metrics.ar.check.active and not self.use_gsr:
            self.warning_pop = WarningPopup()
            self.warning_pop.lab_txt = 'You selected the arousal metric but no GSR device is connected. \nPlease uncheck the Arousal metric or connect a GSR device'
            self.warning_pop.open()
            return False
        else:
            return True

    def check_attention_config(self):
        
        if self.set_sm.metrics.att.check.active and not self.set_sm.metrics.wl.check.active and not self.set_sm.metrics.aw.check.active:
            if self.set_sm.metrics.att.value == '1/BlinkRate' and not int(self.set_sm.processing.ma.value) == 0:
                self.warning_pop = WarningPopup(size_hint=[0.70,0.35])
                self.warning_pop.lab_txt = 'If you want to compute just the attention metric through the BlinkRate, please set the Moving Average Buffer length to 0 in the processing panel'
                self.warning_pop.open()
                return False
            else:
                return True
        else:
            return True

    def write_settings_xml(self):
        
        info_panel = {'id':self.set_sm.general.id_sub.value.lower(),'sess':self.set_sm.general.sess_sub.value,
                    'protocol':self.set_sm.general.prot.value,'visualizationWindow':self.set_sm.general.vis_win.value,
                    'updateFrequency':self.set_sm.general.upd_fr.value,'websocket':self.set_sm.general.ws.check.active}
        processing_panel = {'epoch':self.set_sm.processing.ep.value,'shift':self.set_sm.processing.shift.value,
            'visualMA':self.set_sm.processing.ma.value,'IAF':self.set_sm.processing.iaf.check.active,
            'processingMethod':self.set_sm.processing.proc_method.value, 'blinkMethod': self.set_sm.processing.blink_method.value,
            'filter':self.set_sm.processing.filt.check.active,'HighPass':self.set_sm.processing.lp.value,
            'LowPass':self.set_sm.processing.hp.value,'filter_EOG':self.set_sm.processing.filt_eog.check.active,
            'HighPassEOG':self.set_sm.processing.lp_eog.value,'LowPassEOG':self.set_sm.processing.hp_eog.value,
            'ApplyArtifactRejection':self.set_sm.processing.en_art.check.active,
            'ApplyArtRejThreshold':self.set_sm.processing.en_art_th.check.active,'ArtRejThreshold':self.set_sm.processing.art_th.value,
            'ApplyArtRejDiff':self.set_sm.processing.en_art_diff.check.active,'ArtRejMinDist':self.set_sm.processing.art_diff_min_dist.value}

        str_wl = ','
        str_att = ','
        str_aw = ','
        str_vg = ','
        str_st = ','

        metrics_panel = {}
        if self.set_sm.metrics.wl.check.active:
            metrics_panel['workload'] = {'computationMethod':self.set_sm.metrics.wl.method_value,'compute_on':self.set_sm.metrics.wl.ch_value,
                                'compute_on_nr':str_wl.join([str(ch_nr) for ch_nr in self.set_sm.metrics.wl.ch_list_nr])}
            if self.set_sm.metrics.wl.method_value == 'Raw' or self.set_sm.metrics.wl.method_value == 'Calibrated':
                metrics_panel['workload']['formula'] = self.set_sm.metrics.wl.feat_value
            else:
                metrics_panel['workload']['features'] = self.set_sm.metrics.wl.feat_value

        if self.set_sm.metrics.att.check.active:
            metrics_panel['attention'] = {'computationMethod':self.set_sm.metrics.att.method_value,'compute_on':self.set_sm.metrics.att.ch_value,
                                    'compute_on_nr':str_att.join([str(ch_nr) for ch_nr in self.set_sm.metrics.att.ch_list_nr])}
            if self.set_sm.metrics.att.method_value == 'Raw' or self.set_sm.metrics.att.method_value == 'Calibrated':
                metrics_panel['attention']['formula'] = self.set_sm.metrics.att.feat_value
            else:
                metrics_panel['attention']['features'] = self.set_sm.metrics.att.feat_value

        if self.set_sm.metrics.aw.check.active:
            metrics_panel['approachwithdrawal']= {'computationMethod':self.set_sm.metrics.aw.method_value,'compute_on':self.set_sm.metrics.aw.ch_value,
                                    'compute_on_nr':str_aw.join([str(ch_nr) for ch_nr in self.set_sm.metrics.aw.ch_list_nr])}
            if self.set_sm.metrics.aw.method_value == 'Raw' or self.set_sm.metrics.aw.method_value == 'Calibrated':
                metrics_panel['approachwithdrawal']['formula'] = self.set_sm.metrics.aw.feat_value
            else:
                metrics_panel['approachwithdrawal']['features'] = self.set_sm.metrics.aw.feat_value

        if self.set_sm.metrics.st.check.active:
            metrics_panel['stress']= {'computationMethod':self.set_sm.metrics.st.method_value,'compute_on':self.set_sm.metrics.st.ch_value,
                                    'compute_on_nr':str_st.join([str(ch_nr) for ch_nr in self.set_sm.metrics.st.ch_list_nr])}
            if self.set_sm.metrics.st.method_value == 'Raw' or self.set_sm.metrics.st.method_value == 'Calibrated':
                metrics_panel['stress']['formula'] = self.set_sm.metrics.st.feat_value
            else:
                metrics_panel['stress']['features'] = self.set_sm.metrics.st.feat_value

        if self.set_sm.metrics.vg.check.active:
            metrics_panel['vigilance']= {'computationMethod':self.set_sm.metrics.vg.method_value,'compute_on':self.set_sm.metrics.vg.ch_value,
                                    'compute_on_nr':str_vg.join([str(ch_nr) for ch_nr in self.set_sm.metrics.vg.ch_list_nr])}
            if self.set_sm.metrics.vg.method_value == 'Raw' or self.set_sm.metrics.vg.method_value == 'Calibrated':
                metrics_panel['vigilance']['formula'] = self.set_sm.metrics.vg.feat_value
            else:
                metrics_panel['vigilance']['features'] = self.set_sm.metrics.vg.feat_value

        if self.set_sm.metrics.ar.check.active:
            metrics_panel['arousal'] = {'computationMethod':self.set_sm.metrics.ar.method_value,'formula':self.set_sm.metrics.ar.feat_value,'compute_on':self.set_sm.metrics.ar.ch_value}
            # metrics_panel['arousal']['compute_on_nr'] = str_ar.join([str(ch_nr) for ch_nr in self.set_sm.metrics.ar.ch_list_nr])
        
        jsonString = JSONEncoder().encode({'info':info_panel,'processing':processing_panel,'metrics':metrics_panel})
        xml_str = dicttoxml.dicttoxml(json.loads(jsonString),attr_type=False,root = True,custom_root='general')
        dom = parseString(xml_str)
        
        with open(os.path.join('Data','current_param.xml'), 'w') as out:
            out.write(dom.toprettyxml())
        
        id_sess_name = "{}S{}".format(self.set_sm.general.id_sub.value,self.set_sm.general.sess_sub.value).lower()
        
        savepath = os.path.join("Data",id_sess_name)
        subjects = os.listdir("Data")
        
        if not subjects.__contains__(id_sess_name):
            os.makedirs(savepath)
            os.makedirs(os.path.join(savepath,"CalibrationData"))
        
        with open(os.path.join(savepath,"param.xml"), 'w') as out:
            out.write(dom.toprettyxml())
        
    def read_settings_xml(self):
        if os.path.isfile(os.path.join('Data','current_param.xml')):
            try:
                tree = et.parse(os.path.join('Data','current_param.xml'))
                info = tree.find('info')
                proc = tree.find('processing')
                met = tree.find('metrics')

                self.set_sm.general.id_sub.value = info.find('id').text
                self.set_sm.general.sess_sub.value = info.find('sess').text
                self.set_sm.general.prot.value = info.find('protocol').text
                self.set_sm.general.vis_win.value = info.find('visualizationWindow').text
                self.set_sm.general.upd_fr.value = info.find('updateFrequency').text
                self.set_sm.general.ws.check.active = string2bool(info.find('websocket').text)
                
                self.set_sm.processing.ep.value = proc.find('epoch').text
                self.set_sm.processing.shift.value = proc.find('shift').text
                self.set_sm.processing.ma.value = proc.find('visualMA').text
                self.set_sm.processing.iaf.check.active = string2bool(proc.find('IAF').text)
                self.set_sm.processing.proc_method.value = proc.find('processingMethod').text
                self.set_sm.processing.blink_method.value = proc.find('blinkMethod').text
                self.set_sm.processing.filt.check.active = string2bool(proc.find('filter').text)
                self.set_sm.processing.hp.value = proc.find('LowPass').text
                self.set_sm.processing.lp.value = proc.find('HighPass').text
                self.set_sm.processing.filt_eog.check.active = string2bool(proc.find('filter_EOG').text)
                self.set_sm.processing.hp_eog.value = proc.find('LowPassEOG').text
                self.set_sm.processing.lp_eog.value = proc.find('HighPassEOG').text
                self.set_sm.processing.en_art.check.active = string2bool(proc.find('ApplyArtifactRejection').text)
                self.set_sm.processing.en_art_th.check.active = string2bool(proc.find('ApplyArtRejThreshold').text)
                self.set_sm.processing.art_th.value = proc.find('ArtRejThreshold').text
                self.set_sm.processing.en_art_diff.check.active = string2bool(proc.find('ApplyArtRejDiff').text)
                self.set_sm.processing.art_diff_min_dist.value = proc.find('ArtRejMinDist').text

                wl = met.find('workload')
                if wl:
                    self.set_sm.metrics.wl.check.active = True
                    self.set_sm.metrics.wl.ch_btn.disabled = False
                    self.set_sm.metrics.wl.feat_btn.disabled = False
                    self.set_sm.metrics.wl.method_btn.disabled = False

                    self.set_sm.metrics.wl.method_value = wl.find('computationMethod').text
                    self.set_sm.metrics.wl.ch_value = wl.find('compute_on').text
                    self.set_sm.metrics.wl.ch_list_nr = wl.find('compute_on_nr').text.split(',')

                    if self.set_sm.metrics.wl.method_value == 'Raw' or self.set_sm.metrics.wl.method_value == 'Calibrated':
                        self.set_sm.metrics.wl.feat_value = wl.find('formula').text
                    else: 
                        self.set_sm.metrics.wl.feat_value = wl.find('features').text

                att = met.find('attention')
                if att:
                    self.set_sm.metrics.att.check.active = True
                    self.set_sm.metrics.att.ch_btn.disabled = False
                    self.set_sm.metrics.att.feat_btn.disabled = False
                    self.set_sm.metrics.att.method_btn.disabled = False

                    self.set_sm.metrics.att.method_value = att.find('computationMethod').text
                    self.set_sm.metrics.att.ch_value = att.find('compute_on').text
                    self.set_sm.metrics.att.ch_list_nr = att.find('compute_on_nr').text.split(',')

                    if self.set_sm.metrics.att.method_value == 'Raw' or self.set_sm.metrics.att.method_value == 'Calibrated':
                        self.set_sm.metrics.att.feat_value = att.find('formula').text
                    else: 
                        self.set_sm.metrics.att.feat_value = att.find('features').text

                aw = met.find('approachwithdrawal')
                if aw:
                    self.set_sm.metrics.aw.check.active = True
                    self.set_sm.metrics.aw.ch_btn.disabled = False
                    self.set_sm.metrics.aw.feat_btn.disabled = False
                    self.set_sm.metrics.aw.method_btn.disabled = False

                    self.set_sm.metrics.aw.method_value = aw.find('computationMethod').text
                    self.set_sm.metrics.aw.ch_value = aw.find('compute_on').text
                    self.set_sm.metrics.aw.ch_list_nr = aw.find('compute_on_nr').text.split(',')

                    if self.set_sm.metrics.aw.method_value == 'Raw' or self.set_sm.metrics.aw.method_value == 'Calibrated':
                        self.set_sm.metrics.aw.feat_value = aw.find('formula').text
                    else:
                        self.set_sm.metrics.aw.feat_value = aw.find('features').text

                st = met.find('stress')
                if st:
                    self.set_sm.metrics.st.check.active = True
                    self.set_sm.metrics.st.ch_btn.disabled = False
                    self.set_sm.metrics.st.feat_btn.disabled = False
                    self.set_sm.metrics.st.method_btn.disabled = False

                    self.set_sm.metrics.st.method_value = st.find('computationMethod').text
                    self.set_sm.metrics.st.ch_value = st.find('compute_on').text
                    self.set_sm.metrics.st.ch_list_nr = st.find('compute_on_nr').text.split(',')

                    if self.set_sm.metrics.st.method_value == 'Raw' or self.set_sm.metrics.st.method_value == 'Calibrated':
                        self.set_sm.metrics.st.feat_value = st.find('formula').text
                    else:
                        self.set_sm.metrics.st.feat_value = st.find('features').text

                vg = met.find('vigilance')
                if vg:
                    self.set_sm.metrics.vg.check.active = True
                    self.set_sm.metrics.vg.ch_btn.disabled = False
                    self.set_sm.metrics.vg.feat_btn.disabled = False
                    self.set_sm.metrics.vg.method_btn.disabled = False

                    self.set_sm.metrics.vg.method_value = vg.find('computationMethod').text
                    self.set_sm.metrics.vg.ch_value = vg.find('compute_on').text
                    self.set_sm.metrics.vg.ch_list_nr = vg.find('compute_on_nr').text.split(',')

                    if self.set_sm.metrics.vg.method_value == 'Raw' or self.set_sm.metrics.vg.method_value == 'Calibrated':
                        self.set_sm.metrics.vg.feat_value = vg.find('formula').text
                    else:
                        self.set_sm.metrics.vg.feat_value = vg.find('features').text

                ar = met.find('arousal')
                if ar:
                    self.set_sm.metrics.ar.check.active = True
                    self.set_sm.metrics.ar.ch_btn.disabled = False
                    self.set_sm.metrics.ar.feat_btn.disabled = False
                    self.set_sm.metrics.ar.method_btn.disabled = False

                    self.set_sm.metrics.ar.method_value = ar.find('computationMethod').text
                    self.set_sm.metrics.ar.feat_value = ar.find('formula').text  
                    self.set_sm.metrics.ar.ch_value = ar.find('compute_on').text
            except:
                print("Current Param xml Bad formatting")

    def go_to_general(self):
        self.set_sm.current = 'general'

    def go_to_processing(self):
        self.set_sm.current = 'processing'

    def go_to_metrics(self):
        self.set_sm.current = 'metrics'

class BsrSettingsApp(MDApp):
    
    def build(self):

        sys.path.insert(0,os.path.join(os.getcwd(),'bsr_functions'))
        from utils.settings_class import BSRConfig,EEGConfig # pylint: disable=unresolved-import
        
        l = BSRSettings(BSRConfig('start_config.xml'),EEGConfig('liveAmp'))
        l.read_settings_xml()
        return l

if __name__ == "__main__":

    from widgets.warning_popup import WarningPopup # pylint: disable=unresolved-import
    from widgets.sett_boolean import SettBoolean # pylint: disable=unresolved-import
    from widgets.sett_string import SettString # pylint: disable=unresolved-import
    from widgets.sett_options import SettOptions # pylint: disable=unresolved-import
    from widgets.sett_multioptions import SettMultiOptions # pylint: disable=unresolved-import
    from widgets.sett_spacer import SettSpacer # pylint: disable=unresolved-import
    from widgets.adaptable_boxlayout import AdaptableBoxLayout # pylint: disable=unresolved-import
    from widgets.sett_metric import SettMetric # pylint: disable=unresolved-import

    Builder.load_file('widgets/sett_title.kv')
    Builder.load_file('widgets/sett_button.kv')
    
    BsrSettingsApp().run()

else:

    from screens.widgets.warning_popup import WarningPopup
    from screens.widgets.sett_boolean import SettBoolean
    from screens.widgets.sett_string import SettString
    from screens.widgets.sett_options import SettOptions
    from screens.widgets.sett_multioptions import SettMultiOptions
    from screens.widgets.sett_spacer import SettSpacer
    from screens.widgets.adaptable_boxlayout import AdaptableBoxLayout
    from screens.widgets.sett_metric import SettMetric

    Builder.load_file('screens/widgets/sett_title.kv')
    Builder.load_file('screens/widgets/sett_button.kv')
