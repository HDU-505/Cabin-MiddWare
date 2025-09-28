import xml.etree.ElementTree as et
import os.path

def string2bool(string):
    if string == 'True':
        return True
    else:
        return False

class BSRConfig():
    
    def __init__(self,cfg_file):
        tree = et.parse(os.path.join(cfg_file))
        gen = tree.find('general')
        self.debug = string2bool(gen.find('debug').text)
        self.user = gen.find('user').text
        self.fullscreen = string2bool(gen.find('fullscreen').text)
        self.keyboard = gen.find('keyboardMode').text
        self.device = gen.find('device').text

        self.use_eeg = string2bool(gen.find('EEG').text)
        # if self.use_eeg:
        self.eeg_device = gen.find('EEG_sensor').text
        # else:
        #     self.eeg_device = None
        
        self.use_gsr = string2bool(gen.find('GSR').text)
        # if self.use_gsr:
        self.gsr_device = gen.find('GSR_sensor').text
        # else:
        #     self.gsr_device = None

        self.use_ppg = string2bool(gen.find('PPG').text)
        # if self.use_ppg:
        self.ppg_device = gen.find('PPG_sensor').text
        # else:
        #     self.ppg_device = None

class EEGConfig():

    def __init__(self,device):
        if device == 'liveAmp' or device == 'touch': 
            tree = et.parse(os.path.join('Apps','EegAmpApp','config.cfg'))
        else:
            tree = et.parse(os.path.join('Apps','{}App'.format(device),'config.cfg'))
            
        sett_amp = tree.find('settings')
        chan_amp = tree.find('channels')
        
        self.serial = sett_amp.find('deviceNumber').text
        self.fs = float(sett_amp.find('samplingRate').text)
        self.bs = int(sett_amp.find('chunksize').text)
        self.nr_chann = int(sett_amp.find('channelcount').text)
        
        self.all_ch = []
        self.ch2visualize = []
        self.ch2compute = []
        self.ch2compute_nr = []
        self.eog_ch = None
        self.ch2compute_ndx = 0

        for ch in chan_amp:
            self.all_ch.append(ch.tag)
            if string2bool(ch.find('toVisualize').text):
                self.ch2visualize.append((int(ch.find('nr').text)-1,ch.tag))
            if string2bool(ch.find('toCompute').text):
                self.ch2compute.append((self.ch2compute_ndx,ch.tag))
                self.ch2compute_nr.append(int(ch.find('nr').text)-1)
                # self.ch2compute.append((int(ch.find('nr').text)-1,ch.tag))
                self.ch2compute_ndx += 1
            if string2bool(ch.find('eog').text):
                self.eog_ch = (int(ch.find('nr').text)-1,ch.tag)

class GSRConfig():
    def __init__(self,device):    
        tree = et.parse(os.path.join('Apps','{}App'.format(device),'config.cfg'))
        gen = tree.find('general')

        self.serial = gen.find('serial').text
        self.fs_gsr = float(gen.find('fs_gsr').text)
        self.bs_gsr = int(gen.find('bs_gsr').text)
        # self.ppg = string2bool(gen.find('ppg').text)
        self.fs_ppg = float(gen.find('fs_ppg').text)
        self.bs_ppg = int(gen.find('bs_ppg').text)

class PPGConfig():
    def __init__(self,device):    
        tree = et.parse(os.path.join('Apps','{}App'.format(device),'config.cfg'))
                
        if device == 'shimmer' or device == 'empatica':
            gen = tree.find('general')
            self.serial = gen.find('serial').text
            self.fs_ppg = float(gen.find('fs_ppg').text)
            self.bs_ppg = int(gen.find('bs_ppg').text)

        elif device == 'muse':
            sett_amp = tree.find('settings')
            self.serial = sett_amp.find('deviceNumber').text
            self.fs_ppg = float(sett_amp.find('fs_ppg').text)
            self.bs_ppg = int(sett_amp.find('bs_ppg').text)

class FakeConfig():

    def __init__(self):
        tree = et.parse(os.path.join('Apps','FakeApp','config.cfg'))
        sett_amp = tree.find('settings')
        chan_amp = tree.find('channels')
        
        self.eeg = string2bool(sett_amp.find('eeg').text)
        self.eeg_serial = sett_amp.find('eeg_serial').text
        self.gsr = string2bool(sett_amp.find('gsr').text)
        self.gsr_serial = sett_amp.find('gsr_serial').text
        self.fs_gsr = float(sett_amp.find('fs_gsr').text)
        self.bs_gsr = int(sett_amp.find('bs_gsr').text)
        self.ppg = string2bool(sett_amp.find('ppg').text)
        self.fs_ppg = float(sett_amp.find('fs_ppg').text)
        self.bs_ppg = int(sett_amp.find('bs_ppg').text)

        self.nr_chann = int(sett_amp.find('channelcount').text)
        
        self.ch2visualize = []
        self.ch2compute = []
        self.eog_ch = None
        self.all_ch = []

        for ch in chan_amp:
            self.all_ch.append(ch.tag)
            if string2bool(ch.find('toVisualize').text):
                self.ch2visualize.append((int(ch.find('nr').text)-1,ch.tag))
            if string2bool(ch.find('toCompute').text):
                self.ch2compute.append((int(ch.find('nr').text)-1,ch.tag))
            if string2bool(ch.find('eog').text):
                self.eog_ch = (int(ch.find('nr').text)-1,ch.tag)

class Info():
    def __init__(self):
        self.id_sub = None
        self.sess = None
        self.protocol = None
        self.vis_win = None
        self.upd_freq = None

class Proc():
    def __init__(self):
        self.epoch = None
        self.shift = None
        self.visualMA = None
        self.IAF = None
        self.proc_met = None
        self.blink_met = None
        self.filter_EEG = None
        self.hp = None
        self.lp = None
        self.filter_EOG = None
        self.hp_eog = None
        self.lp_eog = None
        self.apply_artrej = None
        self.apply_artrej_th = None
        self.artrej_th = None
        self.apply_artrej_diff = None
        self.artrej_mindist = None
        self.mean_bin = None
        self.class_metric = None
        self.dec_ndx = None
        self.class_method = None

class AcqConfig():  

    def __init__(self):
        tree = et.parse(os.path.join('Data','current_param.xml'))
        info = tree.find('info')
        proc = tree.find('processing')
        met = tree.find('metrics')
        
        self.info = Info()
        self.info.id = info.find('id').text
        self.info.sess = 'S{}'.format(info.find('sess').text)
        self.info.protocol = info.find('protocol').text
        self.info.vis_win = int(info.find('visualizationWindow').text)
        self.info.upd_freq = int(info.find('updateFrequency').text)
        self.info.ws = string2bool(info.find('websocket').text)
        self.proc = Proc()
        self.proc.epoch = int(proc.find('epoch').text)
        self.proc.shift = int(proc.find('shift').text)
        self.proc.visualMA = int(proc.find('visualMA').text)
        self.proc.IAF = string2bool(proc.find('IAF').text)
        self.proc.proc_met = proc.find('processingMethod').text
        self.proc.blink_met = proc.find('blinkMethod').text
        self.proc.filter_EEG = string2bool(proc.find('filter').text)
        self.proc.hp = int(proc.find('HighPass').text)
        self.proc.lp = int(proc.find('LowPass').text)
        self.proc.filter_EOG = string2bool(proc.find('filter_EOG').text)
        self.proc.hp_eog = int(proc.find('HighPassEOG').text)
        self.proc.lp_eog = int(proc.find('LowPassEOG').text)
        self.proc.apply_artrej = string2bool(proc.find('ApplyArtifactRejection').text)
        self.proc.apply_artrej_th = string2bool(proc.find('ApplyArtRejThreshold').text)
        self.proc.artrej_th = int(proc.find('ArtRejThreshold').text)
        self.proc.apply_artrej_diff = string2bool(proc.find('ApplyArtRejDiff').text)
        self.proc.artrej_mindist = int(proc.find('ArtRejMinDist').text)
        
        metrics = {}
        for m in met:
            metrics['{}'.format(m.tag)] = {'computationMethod':m.find('computationMethod').text}
            if m.find('compute_on_nr') is not None:
                ch2compute = [int(ch) for ch in m.find('compute_on_nr').text.split(',')]
                ch2compute_lab = [ch for ch in m.find('compute_on').text.split(',')]
                metrics['{}'.format(m.tag)]['ch'] = list(zip(ch2compute,ch2compute_lab))

            if m.find('computationMethod').text == 'Raw' or m.find('computationMethod').text == 'Calibrated': 
                metrics['{}'.format(m.tag)]['formula'] = m.find('formula').text
            else:
                metrics['{}'.format(m.tag)]['features']=m.find('features').text

        self.met2compute = metrics

class Bands():
    def __init__(self,IAFt):
        self.Delta = [eval('IAFt-7'),eval('IAFt-6')]
        self.Theta = [eval('IAFt-6'),eval('IAFt-2')]
        self.Alpha = [eval('IAFt-2'),eval('IAFt+2')]
        self.AlphaHigh = [eval('IAFt'),eval('IAFt+2')]
        self.AlphaLow = [eval('IAFt-2'),eval('IAFt')]
        self.Beta = [eval('IAFt+2'),eval('IAFt+16')]
        self.BetaHigh = [eval('IAFt+11'),eval('IAFt+16')]
        self.Gamma = [eval('IAFt+16'),eval('IAFt+30')]

class AcqConfigOff():  

    def __init__(self,user_id):
        tree = et.parse(os.path.join('Data',user_id,'param.xml'))
        info = tree.find('info')
        proc = tree.find('processing')
        met = tree.find('metrics')
        
        self.info = Info()
        self.info.id = info.find('id').text
        self.info.sess = 'S{}'.format(info.find('sess').text)
        self.info.protocol = info.find('protocol').text
        self.info.vis_win = int(info.find('visualizationWindow').text)
        self.info.upd_freq = int(info.find('updateFrequency').text)
        self.info.ws = string2bool(info.find('websocket').text)
        
        self.proc = Proc()
        self.proc.epoch = int(proc.find('epoch').text)
        self.proc.shift = int(proc.find('shift').text)
        self.proc.visualMA = int(proc.find('visualMA').text)
        self.proc.IAF = string2bool(proc.find('IAF').text)
        self.proc.proc_met = proc.find('processingMethod').text
        self.proc.blink_met = proc.find('blinkMethod').text
        self.proc.filter_EEG = string2bool(proc.find('filter').text)
        self.proc.hp = int(proc.find('HighPass').text)
        self.proc.lp = int(proc.find('LowPass').text)
        self.proc.filter_EOG = string2bool(proc.find('filter_EOG').text)
        self.proc.hp_eog = int(proc.find('HighPassEOG').text)
        self.proc.lp_eog = int(proc.find('LowPassEOG').text)
        self.proc.apply_artrej = string2bool(proc.find('ApplyArtifactRejection').text)
        self.proc.apply_artrej_th = string2bool(proc.find('ApplyArtRejThreshold').text)
        self.proc.artrej_th = int(proc.find('ArtRejThreshold').text)
        self.proc.apply_artrej_diff = string2bool(proc.find('ApplyArtRejDiff').text)
        self.proc.artrej_mindist = int(proc.find('ArtRejMinDist').text)
        
        metrics = {}
        for m in met:
            metrics['{}'.format(m.tag)] = {'computationMethod':m.find('computationMethod').text}
            if m.find('compute_on_nr') is not None:
                ch2compute = [int(ch) for ch in m.find('compute_on_nr').text.split(',')]
                ch2compute_lab = [ch for ch in m.find('compute_on').text.split(',')]
                metrics['{}'.format(m.tag)]['ch'] = list(zip(ch2compute,ch2compute_lab))

            if m.find('computationMethod').text == 'Raw' or m.find('computationMethod').text == 'Calibrated': 
                metrics['{}'.format(m.tag)]['formula'] = m.find('formula').text
            else:
                metrics['{}'.format(m.tag)]['features']=m.find('features').text

        self.met2compute = metrics

