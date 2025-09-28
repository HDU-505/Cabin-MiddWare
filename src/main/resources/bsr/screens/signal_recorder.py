import os
import numpy as np
from scipy.signal import butter,lfilter_zi,lfilter
import time
from pylsl import local_clock,resolve_byprop,StreamInlet
import sys

from kivy.app import App
from kivy.core.window import Window 
from kivy.clock import Clock
from kivy.properties import ObjectProperty,StringProperty,NumericProperty,ListProperty

from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout

import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvas # pylint:disable=unresolved-import 

sys.path.insert(0,os.path.join(os.getcwd(),'bsr_functions'))
from utils.settings_class import AcqConfig 

import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)

from screens.widgets.scale_label import ScaleLabel
# from widgets.scale_label import ScaleLabel


class MyFigureCanvas(FigureCanvas):

    def on_touch_down(self, touch):
        Window.release_all_keyboards()

class SignalRecorder(Screen):

    elapsed_time_label = ObjectProperty()
    task = StringProperty('')
    sub_name = StringProperty('')
    marker_number = NumericProperty(0)
    external_dev_bl_lenght = NumericProperty(0.1)
    internal_dev_bl_lenght = NumericProperty(1)
    dev_bl = ObjectProperty()
    dev_battery_img_eeg = ObjectProperty()
    dev_battery_img_gsr = ObjectProperty()

    scope_graph = ObjectProperty()
    low_spinn = ObjectProperty()
    high_spinn = ObjectProperty()
    amplitude_spinn = ObjectProperty()
    start_btn = ObjectProperty()
    start_btn_image = ObjectProperty()
    marker_btn = ObjectProperty()
    home_btn = ObjectProperty()
    imp_btn = ObjectProperty()

    def __init__(self,bsr_cfg,eeg_cfg,gsr_cfg,ppg_cfg, **kwargs):

        super(SignalRecorder, self).__init__(**kwargs)
        self.bsr_cfg = bsr_cfg
        self.eeg_cfg = eeg_cfg
        self.gsr_cfg = gsr_cfg
        self.ppg_cfg = ppg_cfg
        
        # if bsr_cfg.user == 'slave':
        #     self.start_btn.disabled = True
        #     self.marker_btn.disabled = True
            
        self.use_eeg = bsr_cfg.use_eeg
        self.use_gsr = bsr_cfg.use_gsr
        self.use_ppg = bsr_cfg.use_ppg
        
        self.device_list = {}

        '''EEG parameters'''
        self.num_eeg_chann_2Vis = 0
        if self.use_eeg:
            self.channel_vect_2Vis = []
            self.chann_lab_2Vis = []
            self.Fs_EEG = eeg_cfg.fs
            self.block_size_EEG = eeg_cfg.bs
            self.num_eeg_chann = eeg_cfg.nr_chann
            self.device_list[bsr_cfg.eeg_device] = eeg_cfg.serial
            for ch in eeg_cfg.ch2visualize:
                self.channel_vect_2Vis.append(ch[0])
                self.chann_lab_2Vis.append(ch[1])

            self.dt_EEG = 1. / self.Fs_EEG
            self.block_rate_EEG = self.Fs_EEG / self.block_size_EEG
            self.dt_block_EEG = 1. / self.block_rate_EEG
            
            self.num_eeg_chann_2Vis = self.channel_vect_2Vis.__len__()
            
            '''Filter Parameters'''
            self.fn = self.Fs_EEG / 2
            self.f_low = 1
            self.f_high = 15
            self.butter_ord = 4
            self.b, self.a = butter(self.butter_ord, [self.f_low / self.fn, self.f_high / self.fn], btype='band')

            self.zi = lfilter_zi(self.b, self.a)  # Initial condition of the filter
            self.zi_ndim = np.empty((self.zi.size, self.num_eeg_chann))
            for i in range(0, self.num_eeg_chann):
                self.zi_ndim[:, i] = self.zi
        
        '''GSR Parameters'''
        self.num_other_chann = 0
        if self.use_gsr:
            if bsr_cfg.debug:
                self.Fs_gsr = 100
                self.block_size_gsr = 10  
            else:
                self.Fs_gsr = gsr_cfg.fs_gsr
                self.block_size_gsr = gsr_cfg.bs_gsr

            self.device_list[bsr_cfg.gsr_device] = gsr_cfg.serial
            
            self.num_other_chann +=1
            self.dt_gsr = 1. / self.Fs_gsr
            self.block_rate_gsr = int(self.Fs_gsr / self.block_size_gsr)
            self.dt_block_gsr = 1. / self.block_rate_gsr

        '''PPG Parameters'''
        if self.use_ppg:
            if bsr_cfg.debug:
                self.Fs_ppg = 100
                self.block_size_ppg = 10       
            else:
                self.Fs_ppg = ppg_cfg.fs_ppg
                self.block_size_ppg = ppg_cfg.bs_ppg
            
            self.num_other_chann += 1  # ppg
            self.dt_ppg = 1. / self.Fs_ppg
            self.block_rate_ppg = int(self.Fs_ppg / self.block_size_ppg)
            self.dt_block_ppg = 1. / self.block_rate_ppg
    
        self.NUM_CHANN = self.num_eeg_chann_2Vis + self.num_other_chann
        
        '''Device Box Layout'''
        if self.device_list.keys().__len__() == 1:
            self.external_dev_bl_lenght = 0.2
        elif self.device_list.keys().__len__() == 2:
            self.external_dev_bl_lenght = 0.1
        self.internal_dev_bl_lenght = 1-self.external_dev_bl_lenght
        for device in self.device_list.keys():
            device_bl = BoxLayout(spacing=10)    
            if 'liveAmp' in device or 'touch' in device or 'muse' in device: 
                self.dev_battery_img_eeg = Image(source='images/highBattery_icon.png',size_hint_x = 0.1)#, #size=(self.parent.size[0],self.parent.size[1]),pos=(self.parent.pos[0],self.parent.pos[1]),
                device_bl.add_widget(self.dev_battery_img_eeg)
            elif 'shimmer' in device or 'empatica' in device: 
                self.dev_battery_img_gsr = Image(source='images/highBattery_icon.png',size_hint_x = 0.1)
                device_bl.add_widget(self.dev_battery_img_gsr)
            dev_label = ScaleLabel(text='{} {}'.format(device,self.device_list[device]),font_size= "25dp",size_hint_x = 0.9,halign='left',valign='middle') #text_size= self.texture_size,
            dev_label.bind(size=dev_label.setter('text_size')) 
            device_bl.add_widget(dev_label)
            self.dev_bl.add_widget(device_bl)

        if not self.use_eeg or bsr_cfg.eeg_device == 'muse':
            self.imp_btn.disabled = True

        self.plot_color = (float(189) / 255, float(218) / 255, float(237) / 255) #celeste
        self.blueBS = (float(25)/255,float(63)/255,float(90)/255)
        '''Plot initialization'''
        plt.rcParams.update({'figure.autolayout': False})  # to make the figure fullfill the screen
        self.fig = plt.figure()
        self.fig.patch.set_facecolor(self.blueBS)

        self.can = MyFigureCanvas(self.fig)
        self.can.draw()

        self.scope_graph.add_widget(self.can)

    def open_taskName_popup(self):
        self.taskName_popup = TaskName()
        self.taskName_popup.open()
        self.taskName_popup.bind(on_dismiss=self.set_run_name)
    
    def set_run_name(self,obj):
        self.task = self.taskName_popup.run_name

    def on_enter(self):

        self.acq_cfg = AcqConfig()
        self.sub_name = self.acq_cfg.info.id
        self.warning_pop_opened = False
        self.warning_pop_opened_battery = False

        ' Visualization Parameters'
        self.vis_window = self.acq_cfg.info.vis_win  # seconds
        self.vis_update_freq = self.acq_cfg.info.upd_freq  # seconds
        ' Buffer initialization'
        '''EEG'''
        if self.use_eeg:
            self.buf_size_EEG = self.vis_window * int(self.Fs_EEG)  # 10 seconds of data
            self.eeg_buff = np.empty((self.buf_size_EEG, self.num_eeg_chann), float)
            self.eeg_buff.fill(np.nan)  #

            self.time_EEG = np.linspace(1, self.buf_size_EEG,
                                        self.buf_size_EEG) * self.dt_EEG
        '''GSR Sensor'''
        if self.use_gsr:
            self.buf_size_gsr = self.vis_window * int(self.Fs_gsr)  # 10 seconds of data
            self.gsr_buff = np.empty((self.buf_size_gsr, 1), float)
            self.gsr_buff.fill(np.nan)  # np.nan
            self.time_gsr = np.linspace(1, self.buf_size_gsr,
                                        self.buf_size_gsr) * self.dt_gsr
        '''PPG Sensor'''
        if self.use_ppg:
            self.buf_size_ppg = self.vis_window * int(self.Fs_ppg)  # 10 seconds of data
            self.ppg_buff = np.empty((self.buf_size_ppg, 1), float)
            self.ppg_buff.fill(np.nan)  # np.nan
            self.time_ppg = np.linspace(1, self.buf_size_ppg,
                                        self.buf_size_ppg) * self.dt_ppg
        
        self.initialize_plot()
        self.start_plot_events()

    def initialize_plot(self):

        yprops = dict(rotation=0,
                      horizontalalignment='right',
                      verticalalignment='center',
                      x=-0.01, fontsize=15,color='white')
        axprops = dict(yticks=[],facecolor=self.plot_color)

        self.ax = []
        self.line = []

        spacing = 0.8 / self.NUM_CHANN

        self.y_lim_min = -200
        self.y_lim_max = 200

        if not self.use_eeg:
            for i in range(0, self.NUM_CHANN):
                self.ax.append(self.fig.add_axes([0.05, 0.9 - spacing * (i + 1), 0.9, spacing], **axprops))
                if (self.use_gsr and not self.use_ppg) or (self.use_ppg and not self.use_gsr):
                    if self.use_gsr:
                        self.line_temp, = self.ax[i].plot(self.time_gsr, self.gsr_buff, lw=1,
                                                        color=[float(233) / 255, float(147) / 255, float(34) / 255])
                        self.line.append(self.line_temp)
                        self.ax[i].set_ylabel('GSR', **yprops)
                        self.ax[i].set_ylim(1, 3)
                        self.ax[i].set_xlim(self.time_gsr[0], self.time_gsr[-1])
                    elif self.use_ppg:
                        self.line_temp, = self.ax[i].plot(self.time_ppg, self.ppg_buff, lw=1, color='chocolate')
                        self.line.append(self.line_temp)
                        self.ax[i].set_ylabel('PPG', **yprops)
                        self.ax[i].set_xlim(self.time_ppg[0], self.time_ppg[-1])
                elif self.use_gsr and self.use_ppg:
                    if i == 0:
                        self.line_temp, = self.ax[i].plot(self.time_gsr, self.gsr_buff, lw=1,
                                                        color=[float(233) / 255, float(147) / 255, float(34) / 255])
                        self.line.append(self.line_temp)
                        self.ax[i].set_ylabel('GSR', **yprops)
                        self.ax[i].set_ylim(1, 3)
                        self.ax[i].set_xlim(self.time_gsr[0], self.time_gsr[-1])
                    if i == 1:
                        self.line_temp, = self.ax[i].plot(self.time_ppg, self.ppg_buff, lw=1, color='chocolate')
                        self.line.append(self.line_temp)
                        self.ax[i].set_ylabel('PPG', **yprops)
                        self.ax[i].set_xlim(self.time_ppg[0], self.time_ppg[-1])
        else:
            for i in range(0, self.NUM_CHANN):
                self.ax.append(self.fig.add_axes([0.05, 0.9 - spacing * (i + 1), 0.9, spacing], **axprops))
                if i < self.num_eeg_chann_2Vis:
                    self.line_temp, = self.ax[i].plot(self.time_EEG, self.eeg_buff[:, self.channel_vect_2Vis[i]], lw=0.7,color=self.blueBS)
                    self.line.append(self.line_temp)
                    self.ax[i].set_ylabel(self.chann_lab_2Vis[i], **yprops)
                    self.ax[i].set_ylim(self.y_lim_min, self.y_lim_max)
                    self.ax[i].set_xlim(self.time_EEG[0], self.time_EEG[-1])
                if i >= self.num_eeg_chann_2Vis:
                    if (self.use_gsr and not self.use_ppg) or (self.use_ppg and not self.use_gsr):
                        if self.use_gsr:
                            self.line_temp, = self.ax[i].plot(self.time_gsr, self.gsr_buff, lw=1,
                                                            color=[float(233) / 255, float(147) / 255, float(34) / 255])
                            self.line.append(self.line_temp)
                            self.ax[i].set_ylabel('GSR', **yprops)
                            self.ax[i].set_ylim(1, 3)
                            self.ax[i].set_xlim(self.time_gsr[0], self.time_gsr[-1])
                        elif self.use_ppg:
                            self.line_temp, = self.ax[i].plot(self.time_ppg, self.ppg_buff, lw=1, color='chocolate')
                            self.line.append(self.line_temp)
                            self.ax[i].set_ylabel('PPG', **yprops)
                            self.ax[i].set_xlim(self.time_ppg[0], self.time_ppg[-1])
                    elif self.use_gsr and self.use_ppg:
                        if i == self.num_eeg_chann_2Vis:  # if use gsr
                            self.line_temp, = self.ax[i].plot(self.time_gsr, self.gsr_buff, lw=1,
                                                            color=[float(233) / 255, float(147) / 255, float(34) / 255])
                            self.line.append(self.line_temp)
                            self.ax[i].set_ylabel('GSR', **yprops)
                            self.ax[i].set_ylim(1, 3)
                            self.ax[i].set_xlim(self.time_gsr[0], self.time_gsr[-1])
                        if i == self.num_eeg_chann_2Vis + 1:  # if use gsr and ppg on
                            self.line_temp, = self.ax[i].plot(self.time_ppg, self.ppg_buff, lw=1, color='chocolate')
                            self.line.append(self.line_temp)
                            self.ax[i].set_ylabel('PPG', **yprops)
                            self.ax[i].set_xlim(self.time_ppg[0], self.time_ppg[-1])

        self.ax[0].set_title("Not Recording", fontsize=20, color='red')

        self.ax[-1].tick_params(axis='x', labelsize=15)
        # turn off x ticklabels for all but the lower axes
        for ax in self.ax:
            ax.tick_params(color=self.blueBS, labelcolor=self.blueBS)
            for spine in ax.spines.values():
                spine.set_edgecolor(self.plot_color)

        self.ax[-1].spines['bottom'].set_color(self.plot_color)
        self.ax[-1].tick_params(color=self.plot_color, labelcolor='white')

        self.can.draw()
        
        self.idx_EEG = 0  # Buffer Index
        self.idx_GSR = 0
        self.idx_PPG = 0
        # self.idx_TMP = 0

        self.founded_eeg = False
        self.founded_eeg_bat = False
        self.founded_gsr = False
        self.founded_gsr_bat = False
        self.founded_ppg = False

        self.inlet_eeg = None
        self.inlet_gsr = None
        self.inlet_ppg = None
        self.inlet_eeg_bat = None
        self.inlet_gsr_bat = None

        if self.use_eeg:
            self.previuos_low = self.f_low
            self.previuos_high = self.f_high

        if not self.bsr_cfg.use_eeg or self.bsr_cfg.debug:
            self.eeg_flag = True
        else:
            self.eeg_flag = False

        self.start_eeg = 0
        self.start_gsr = 0
        self.start_ppg = 0

    def start_plot_events(self):
        if self.use_eeg:
            self.upd_scope_event_eeg = Clock.schedule_interval(self.update_scope_eeg,self.dt_block_EEG)
            self.update_battery_eeg_evt = Clock.schedule_interval(self.update_battery_eeg,5)
        if self.use_gsr:
            self.upd_scope_event_gsr = Clock.schedule_interval(self.update_scope_gsr, self.dt_block_gsr)
            self.update_battery_gsr_evt = Clock.schedule_interval(self.update_battery_gsr,10)
        if self.use_ppg:
            self.upd_scope_event_ppg = Clock.schedule_interval(self.update_scope_ppg,self.dt_block_ppg)
        
        self.upd_canvas_evt = Clock.schedule_interval(self.update_canvas, 1/self.vis_update_freq)

    def update_canvas(self, dt):

        self.can.draw()

    def update_scope_eeg(self, dt):

        if self.founded_eeg:
            sample_EEG, timestamps = self.inlet_eeg.pull_chunk(timeout=0.0,max_samples=100)
            print("time: " + timestamps)

            if timestamps and not self.eeg_flag:
                self.eeg_flag = True

            if timestamps:
                np_sample_eeg = np.asarray(sample_EEG)

                if self.bsr_cfg.eeg_device == 'liveAmp' or self.bsr_cfg.eeg_device == 'touch':
                    if not np.diff(np_sample_eeg[:,0]).nonzero()[0].any() and not self.warning_pop_opened and np_sample_eeg[:,0].nonzero()[0].any():
                        self.warning_pop = WarningPopup()
                        self.warning_pop.lab_txt = 'Amplifier Disconnected! Plese check the Amplifier'
                        self.warning_pop.open()
                        self.warning_pop_opened = True

                filtered_array, self.zi_ndim = lfilter(self.b, self.a, np_sample_eeg, axis=0,
                                                            zi=self.zi_ndim)

                '''Buffer Update'''
                extra = self.idx_EEG+np_sample_eeg.shape[0] - self.buf_size_EEG
                if extra>0:
                    self.eeg_buff[:self.idx_EEG,:]= np.nan
                    self.eeg_buff[self.idx_EEG:,:] = np.nan 
                    self.eeg_buff[0:extra,:] = filtered_array[-extra:,:] 
                    self.idx_EEG = extra
                    print('EEG {}'.format(time.time() -self.start_eeg))
                    self.start_eeg = time.time()
                else:
                    self.eeg_buff[self.idx_EEG:self.idx_EEG+np_sample_eeg.shape[0],:] = filtered_array
                    self.idx_EEG = self.idx_EEG+np_sample_eeg.shape[0]

                for ii in range(0, self.num_eeg_chann_2Vis):
                    self.line[ii].set_ydata(self.eeg_buff[:, self.channel_vect_2Vis[ii]])

        else:
            ''' Looking for the inlet'''
            if not self.bsr_cfg.debug:
                self.eeg_streams = resolve_byprop('name', '{}_EEG'.format(self.eeg_cfg.serial), timeout=0.0)
            else:
                self.eeg_streams = resolve_byprop('type', 'EEG',timeout=0.0)

            if self.eeg_streams.__len__() != 0:
                self.inlet_eeg = StreamInlet(self.eeg_streams[0])
                self.founded_eeg = True

    def update_battery_eeg(self,dt):
        if self.founded_eeg_bat:
            sample_bat, timestamp = self.inlet_eeg_bat.pull_sample(timeout=0.0)

            if sample_bat:
                # print(sample_bat[0])
                if self.bsr_cfg.eeg_device == 'liveAmp':
                    if sample_bat[0] == 3:
                        self.dev_battery_img_eeg.source = 'images/highBattery_icon.png'
                    elif sample_bat[0] == 2:
                        self.dev_battery_img_eeg.source = 'images/medLowBattery_icon.png'
                        if not self.warning_pop_opened_battery: 
                            self.warning_pop = WarningPopup()
                            self.warning_pop.lab_txt = 'The amplifier battery is low. Approximately 10 minutes remaining'
                            self.warning_pop.open()
                            self.warning_pop_opened_battery = True

                    elif sample_bat[0] == 1:
                        self.dev_battery_img_eeg.source = 'images/lowBattery_icon.png'

                elif self.bsr_cfg.eeg_device == 'touch':
                    if  sample_bat[0] >= 3550: 
                        self.dev_battery_img_eeg.source = 'images/highBattery_icon.png'
                    elif sample_bat[0] >= 3400 and sample_bat[0] < 3550: 
                        self.dev_battery_img_eeg.source = 'images/medBattery_icon.png'
                    elif sample_bat[0] >= 3330 and sample_bat[0] < 3400: 
                        self.dev_battery_img_eeg.source = 'images/medLowBattery_icon.png'
                        if not self.warning_pop_opened_battery: 
                            self.warning_pop = WarningPopup()
                            self.warning_pop.lab_txt = 'The amplifier battery is low. Approximately 10 minutes remaining'
                            self.warning_pop.open()
                            self.warning_pop_opened_battery = True

                    elif sample_bat[0] < 3300:
                        self.dev_battery_img_eeg.source = 'images/lowBattery_icon.png'
                        
                elif self.bsr_cfg.eeg_device == 'muse':
                    if sample_bat[0] <= 100.0 and sample_bat[0] >= 75.0: 
                        self.dev_battery_img_eeg.source = 'images/highBattery_icon.png'
                    elif sample_bat[0] < 75.0 and sample_bat[0] >= 50.0: 
                        self.dev_battery_img_eeg.source = 'images/medBattery_icon.png'
                    elif sample_bat[0] < 50.0 and sample_bat[0] >= 25.0: 
                        self.dev_battery_img_eeg.source = 'images/medLowBattery_icon.png'
                    elif sample_bat[0] < 25.0:
                        self.dev_battery_img_eeg.source = 'images/lowBattery_icon.png'

        else:
            ''' Looking for the inlet'''
            if not self.bsr_cfg.debug:
                self.eeg_bat_streams = resolve_byprop('name', '{}_EEG_Battery'.format(self.eeg_cfg.serial), timeout=0.0)

                if self.eeg_streams.__len__() != 0:
                    self.inlet_eeg_bat = StreamInlet(self.eeg_bat_streams[0])
                    self.founded_eeg_bat = True

    def update_scope_gsr(self,dt):
        if self.founded_gsr:
            samples_GSR, timestamps = self.inlet_gsr.pull_chunk(timeout=0.0)

            if self.eeg_flag:                
                if timestamps:
                    ''' Buffer Update'''
                    np_samples_gsr = np.asarray(samples_GSR)
                    extra = self.idx_GSR+np_samples_gsr.shape[0] - self.buf_size_gsr

                    if extra>0:
                        self.gsr_buff[:self.idx_GSR,:]= np.nan
                        self.gsr_buff[self.idx_GSR:,:] = np.nan 
                        self.gsr_buff[0:extra,:] = np_samples_gsr[-extra:,:] 
                        self.idx_GSR = extra
                        print('GSR {}'.format(time.time() -self.start_gsr))
                        self.start_gsr = time.time()
                    else:
                        self.gsr_buff[self.idx_GSR:self.idx_GSR+np_samples_gsr.shape[0],:] = np_samples_gsr
                        self.idx_GSR = self.idx_GSR+np_samples_gsr.shape[0]

                    
                    self.inf_lim_gsr = np.nanpercentile(self.gsr_buff, 1, axis=0)
                    self.sup_lim_gsr = np.nanpercentile(self.gsr_buff, 100, axis=0)

                    if self.use_ppg:
                        if not np.isnan(self.inf_lim_gsr).any() and not np.isnan(self.sup_lim_gsr).any():
                            self.ax[-2].set_ylim(self.inf_lim_gsr - 0.05, self.sup_lim_gsr + 0.05)
                        self.line[-2].set_ydata(self.gsr_buff)
                    else:
                        if not np.isnan(self.inf_lim_gsr).any() and not np.isnan(self.sup_lim_gsr).any():
                            self.ax[-1].set_ylim(self.inf_lim_gsr - 0.05, self.sup_lim_gsr + 0.05)
                        self.line[-1].set_ydata(self.gsr_buff)

        else:
            ''' Looking for the inlet'''
            if not self.bsr_cfg.debug:
                self.gsr_streams = resolve_byprop('name', '{}_GSR'.format(self.gsr_cfg.serial), timeout=0.0)
            else:
                self.gsr_streams = resolve_byprop('name', 'fake_GSR',timeout=0.0)

            if self.gsr_streams.__len__() != 0:
                self.inlet_gsr = StreamInlet(self.gsr_streams[0])
                self.founded_gsr = True

    def update_battery_gsr(self,dt):
        if self.founded_gsr_bat:
            sample_bat, timestamp = self.inlet_gsr_bat.pull_sample(timeout=0.0)

            if sample_bat:

                # print(sample_bat[0])
                if self.bsr_cfg.gsr_device == 'shimmer':
                    if sample_bat[0] <= 4167 and sample_bat[0] >= 3933: 
                        self.dev_battery_img_gsr.source = 'images/highBattery_icon.png'
                    elif sample_bat[0] < 3933 and sample_bat[0] >= 3803: 
                        self.dev_battery_img_gsr.source = 'images/medBattery_icon.png'
                    elif sample_bat[0] < 3803 and sample_bat[0] >= 3717: 
                        self.dev_battery_img_gsr.source = 'images/medLowBattery_icon.png'
                    elif sample_bat[0] < 3717:
                        self.dev_battery_img_gsr.source = 'images/lowBattery_icon.png'
                elif self.bsr_cfg.gsr_device == 'empatica':
                    if sample_bat[0] <= 1.0 and sample_bat[0] >= 0.75: 
                        self.dev_battery_img_gsr.source = 'images/highBattery_icon.png'
                    elif sample_bat[0] < 0.75 and sample_bat[0] >= 0.5: 
                        self.dev_battery_img_gsr.source = 'images/medBattery_icon.png'
                    elif sample_bat[0] < 0.5 and sample_bat[0] >= 0.25: 
                        self.dev_battery_img_gsr.source = 'images/medLowBattery_icon.png'
                    elif sample_bat[0] < 0.25:
                        self.dev_battery_img_gsr.source = 'images/lowBattery_icon.png'

        else:
            ''' Looking for the inlet'''
            if not self.bsr_cfg.debug:
                self.gsr_bat_streams = resolve_byprop('name', '{}_GSR_Battery'.format(self.gsr_cfg.serial), timeout=0.0)
                if self.gsr_bat_streams.__len__() != 0:
                    self.inlet_gsr_bat = StreamInlet(self.gsr_bat_streams[0])
                    self.founded_gsr_bat = True

    def update_scope_ppg(self,dt):
        if self.founded_ppg:

            sample_PPG, timestamps = self.inlet_ppg.pull_chunk(timeout=0.0)

            if self.eeg_flag:
                
                if timestamps:
                    ''' Buffer Update'''
                    np_samples_ppg = np.asarray(sample_PPG)
                    extra = self.idx_PPG+np_samples_ppg.shape[0] - self.buf_size_ppg

                    if extra>0:
                        self.ppg_buff[:self.idx_PPG,:]= np.nan
                        self.ppg_buff[self.idx_PPG:,:] = np.nan 
                        self.ppg_buff[0:extra,:] = np_samples_ppg[-extra:,:] 
                        self.idx_PPG = extra
                        print('PPG {}'.format(time.time() -self.start_ppg))
                        self.start_ppg = time.time()
                    else:
                        self.ppg_buff[self.idx_PPG:self.idx_PPG+np_samples_ppg.shape[0],:] = np_samples_ppg
                        self.idx_PPG = self.idx_PPG+np_samples_ppg.shape[0]
                    
                    self.inf_lim_ppg = np.nanpercentile(self.ppg_buff, 1, axis=0)
                    self.sup_lim_ppg = np.nanpercentile(self.ppg_buff, 100, axis=0)

                    if not np.isnan(self.inf_lim_ppg).any() and not np.isnan(self.sup_lim_ppg).any():
                        self.ax[-1].set_ylim(self.inf_lim_ppg, self.sup_lim_ppg)
                    self.line[-1].set_ydata(self.ppg_buff)

        else:
            ''' Looking for the inlet'''
            if not self.bsr_cfg.debug:
                self.ppg_streams = resolve_byprop('name', '{}_PPG'.format(self.ppg_cfg.serial), timeout=0.0)
            else:
                self.ppg_streams = resolve_byprop('name', 'fake_PPG',timeout=0.0)

            if self.ppg_streams.__len__() != 0:
                self.inlet_ppg = StreamInlet(self.ppg_streams[0])
                self.founded_ppg = True

    def send_start(self):

        if self.start_btn_image.source == os.path.join('images','start_icon_2.png'):

            self.ax[0].set_title("Recording...", fontsize=20, color='green')
            self.start_time = time.time()
            self.timer_evt = Clock.schedule_interval(self.acq_timer, 1.0 / 2)

            self.start_btn_image.source = os.path.join('images','stop_icon_2.png')

            self.start_btn.disabled = True
            Clock.schedule_once(self.enableafter1second_start, 1)

            self.marker_btn.disabled = False
            self.imp_btn.disabled = True
            self.home_btn.disabled = True

        elif self.start_btn_image.source == os.path.join('images','stop_icon_2.png'):

            if self.timer_evt:
                self.timer_evt.cancel()

            self.ax[0].set_title("Not Recording", fontsize=20, color='red')
            self.elapsed_time_label.text = '00:00:00'
            self.marker_number = 0
            self.start_btn_image.source = os.path.join('images','start_icon_2.png')

            self.start_btn.disabled = True
            Clock.schedule_once(self.enableafter1second_start, 1)

            if self.use_eeg and not self.bsr_cfg.eeg_device=='muse':
                self.imp_btn.disabled = False

            self.marker_btn.disabled = True
            self.home_btn.disabled = False
        
    def acq_timer(self, dt):

        self.elapsed_time = time.time() - self.start_time
        hours, rem = divmod(self.elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        self.elapsed_time_label.text = "{:0>2}:{:0>2}:{:0>2d}".format(int(hours),int(minutes), int(seconds))

    def send_marker(self):

        self.marker_number = self.marker_number + 1

        self.marker_btn.disabled = True
        Clock.schedule_once(self.enableafter1second, 1)

    def enableafter1second(self, dt):
        # if self.bsr_cfg.user == 'master':
        self.marker_btn.disabled = False

    def enableafter1second_start(self, dt):
        # if self.bsr_cfg.user == 'master':
        self.start_btn.disabled = False

    def send_impedance_check(self):

        self.cancel_all_events()
        self.close_all_streams()
        self.clear_plots()

        self.id_sub = self.acq_cfg.info.id
        self.sess = self.acq_cfg.info.sess
        self.id_sess_name = "{}{}".format(self.id_sub, self.sess)

        self.imp_popup = ImpedancePopup(self.id_sess_name,self.bsr_cfg,self.eeg_cfg)
        self.imp_popup.open() 

    def stop_impedance_check(self):
        self.imp_popup.dismiss()
        self.start_plot_events()

    def clear_plots(self):

        self.idx_EEG = 0  # Buffer Index
        self.idx_GSR = 0
        self.idx_PPG = 0
        # self.idx_TMP = 0

        self.start_eeg = 0
        self.start_gsr = 0
        self.start_ppg = 0

        ' Buffer initialization'
        '''EEG'''
        if self.use_eeg:
            self.eeg_buff = np.empty((self.buf_size_EEG, self.num_eeg_chann), float)
            self.eeg_buff.fill(np.nan)  #
            for ii in range(0, self.num_eeg_chann_2Vis):
                self.line[ii].set_ydata(self.eeg_buff[:, self.channel_vect_2Vis[ii]])
        '''GSR Sensor'''
        if self.use_gsr:
            self.gsr_buff = np.empty((self.buf_size_gsr, 1), float)
            self.gsr_buff.fill(np.nan)  # np.nan
            if self.use_ppg:
                self.line[-2].set_ydata(self.gsr_buff)
            else:
                self.line[-1].set_ydata(self.gsr_buff)
        '''PPG Sensor'''
        if self.use_ppg:
            self.ppg_buff = np.empty((self.buf_size_ppg, 1), float)
            self.ppg_buff.fill(np.nan)  # np.nan
            self.line[-1].set_ydata(self.ppg_buff)

        self.can.draw()

    def autoscale(self):

        if self.amplitude_spinn.text == 'auto':
            if self.use_eeg:
                array_min = np.nanmin(self.eeg_buff, axis=0)
                array_max = np.nanmax(self.eeg_buff, axis=0)
                self.y_lim_min = array_min
                self.y_lim_max = array_max
                try:
                    for i in range(0, self.num_eeg_chann_2Vis):
                        self.ax[i].set_ylim(self.y_lim_min[i], self.y_lim_max[i])
                except:
                    print('all NaN')
        else:
            if self.use_eeg:
                self.y_lim_min = int('-{}'.format(self.amplitude_spinn.text)) / 2
                self.y_lim_max = int(self.amplitude_spinn.text) / 2
                for i in range(0, self.num_eeg_chann_2Vis):
                    self.ax[i].set_ylim(self.y_lim_min, self.y_lim_max)

    def set_low_cutoff_filter(self):
        if self.use_eeg:
            if self.high_spinn.text == "High Cutoff":
                self.f_high = self.previuos_high
            else:
                self.f_high = float(self.high_spinn.text)

            self.f_low = float(self.low_spinn.text)
            self.butter_ord = 4
            #         print self.f_low,self.f_high
            self.b, self.a = butter(self.butter_ord, [self.f_low / self.fn, self.f_high / self.fn], btype='band')

            self.zi = lfilter_zi(self.b, self.a)  # Initial condition of the filter
            self.zi_ndim = np.empty((self.zi.size, self.num_eeg_chann))
            for i in range(0, self.num_eeg_chann):
                self.zi_ndim[:, i] = self.zi

            self.previuos_low = float(self.low_spinn.text)

    def set_high_cutoff_filter(self):
        if self.use_eeg:
            if self.low_spinn.text == "Low Cutoff":
                self.f_low = self.previuos_low
            else:
                self.f_low = float(self.low_spinn.text)

            self.f_high = float(self.high_spinn.text)
            self.butter_ord = 4
            self.b, self.a = butter(self.butter_ord, [self.f_low / self.fn, self.f_high / self.fn], btype='band')

            self.zi = lfilter_zi(self.b, self.a)  # Initial condition of the filter
            self.zi_ndim = np.empty((self.zi.size, self.num_eeg_chann))
            for i in range(0, self.num_eeg_chann):
                self.zi_ndim[:, i] = self.zi

            self.previuos_high = float(self.high_spinn.text)

    def cancel_all_events(self):
        if self.use_eeg:
            if self.upd_scope_event_eeg:
                self.upd_scope_event_eeg.cancel()
                self.update_battery_eeg_evt.cancel()
            self.eeg_flag = False
        if self.use_gsr:
            if self.upd_scope_event_gsr:
                self.upd_scope_event_gsr.cancel()
                self.update_battery_gsr_evt.cancel()
        if self.use_ppg:
            if self.upd_scope_event_ppg: 
                self.upd_scope_event_ppg.cancel()
        if self.upd_canvas_evt:
            self.upd_canvas_evt.cancel()

    def close_all_streams(self):

        if self.use_eeg:
            if self.inlet_eeg:
                self.inlet_eeg.close_stream()
            if not self.bsr_cfg.debug:
                if self.inlet_eeg_bat:
                    self.inlet_eeg_bat.close_stream()
            self.founded_eeg = False
            self.founded_eeg_bat = False
        if self.use_gsr:
            if self.inlet_gsr:
                self.inlet_gsr.close_stream()
            if not self.bsr_cfg.debug:
                if self.inlet_gsr_bat:
                    self.inlet_gsr_bat.close_stream()
            self.founded_gsr = False
            self.founded_gsr_bat = False
        if self.use_ppg:
            if self.inlet_ppg:
                self.inlet_ppg.close_stream()
            self.founded_ppg = False

    def on_leave(self):

        self.clear_plots()
        self.task = ''
        self.founded_eeg = False
        self.founded_eeg_bat = False
        self.founded_gsr = False
        self.founded_gsr_bat = False
        self.founded_ppg = False

    def back_home_from_sr(self):
        print("Home")

class SignalRecorderSM(ScreenManager):
    
    sr = ObjectProperty()

    def __init__(self, **kwargs):

        super(SignalRecorderSM, self).__init__(**kwargs)
        sys.path.insert(0,os.path.join(os.getcwd(),'bsr_functions'))
        from utils.settings_class import BSRConfig,AcqConfig,EEGConfig,GSRConfig,PPGConfig # pylint: disable=unresolved-import

        self.sr = SignalRecorder(BSRConfig('start_config.xml'),EEGConfig('liveAmp'),GSRConfig('shimmer'),PPGConfig('shimmer'),name='sr')
        self.add_widget(self.sr)
        self.current = 'sr'

    def send_start(self):
        self.sr.send_start()

    def send_impedance_check(self):
        self.sr.send_impedance_check()

    def stop_impedance_check(self):
        self.sr.stop_impedance_check()

    def send_marker(self):
        self.sr.send_marker()

    def back_home_from_sr(self):
        self.sr.back_home_from_sr()

class SignalRecorderApp(App):

    def build(self):

        l = SignalRecorderSM()
        return l

if __name__ == "__main__":

    from widgets.orange_spacer import OrangeSpacer
    from widgets.scale_label import ScaleLabel
    from widgets.warning_popup import WarningPopup
    from widgets.impedance_popup import ImpedancePopup
    from widgets.taskName_popup import TaskName
    from widgets.acquire_button import AcquireButton
    
    SignalRecorderApp().run()

else:

    from screens.widgets.orange_spacer import OrangeSpacer
    from screens.widgets.scale_label import ScaleLabel
    from screens.widgets.warning_popup import WarningPopup
    from screens.widgets.impedance_popup import ImpedancePopup
    from screens.widgets.taskName_popup import TaskName
    from screens.widgets.acquire_button import AcquireButton