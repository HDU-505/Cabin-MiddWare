'''
Created on 13 lug 2017

@author: Anto
'''

from asyncio.windows_events import NULL
import os
import os.path
from json.encoder import JSONEncoder
from socket import create_connection
from time import sleep
from tkinter.tix import Tree
from unittest import result
from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_byprop, local_clock
import numpy as np
import json
from utils.settings_class import BSRConfig,EEGConfig,GSRConfig,PPGConfig,AcqConfig
from kivy.config import Config
import ctypes
import platform
import psutil 
import websocket

for interface in psutil.net_if_addrs():
    if psutil.net_if_addrs()[interface][0].address:
        mac = psutil.net_if_addrs()[interface][0].address
        break

''' Connection Settings'''
bsr_cfg = BSRConfig("start_config.xml")
use_eeg = bsr_cfg.use_eeg
use_gsr = bsr_cfg.use_gsr
use_ppg = bsr_cfg.use_ppg

eeg_cfg = EEGConfig(bsr_cfg.eeg_device)
gsr_cfg = GSRConfig(bsr_cfg.gsr_device)
ppg_cfg = PPGConfig(bsr_cfg.ppg_device)



if use_eeg:
    # if bsr_cfg.eeg_device == 'liveAmp' or bsr_cfg.eeg_device == 'touch':
    '''Outlet that Sends commands to the EEG Amp App Controller'''
    info_command2EEGapp = StreamInfo('CommandFromGui_{}'.format(eeg_cfg.serial), 'Markers', 1, 0, 'string', 'myuidw43536')
    print('CommandFromGui_{}'.format(eeg_cfg.serial))
    outlet_command2EEGapp = StreamOutlet(info_command2EEGapp)

if use_gsr:
    # if bsr_cfg.gsr_device == 'shimmer':
    '''Outlet that Sends commands to the Shimmer App Controller'''
    info_commandToGsrApp = StreamInfo('CommandFromGui_{}'.format(gsr_cfg.serial), 'Markers', 1, 0, 'string', 'myuidw43536')
    outlet_commandToGsrApp = StreamOutlet(info_commandToGsrApp)

if use_ppg:
    # if bsr_cfg.ppg_device == 'shimmer':
    if not use_gsr:
        '''Outlet that Sends commands to the Shimmer App Controller'''
        info_commandToGsrApp = StreamInfo('CommandFromGui_{}'.format(ppg_cfg.serial), 'Markers', 1, 0, 'string', 'myuidw43536')
        outlet_commandToGsrApp = StreamOutlet(info_commandToGsrApp)

if bsr_cfg.debug:
    info_commandToFakeApp = StreamInfo('CommandFromGui_fake', 'Markers', 1, 0, 'string', 'myuidw43536')
    outlet_commandToFakeApp = StreamOutlet(info_commandToFakeApp)

    if platform.system() == 'Windows':
        os.chdir("Batch")
        os.system("start /min startFakeServer.bat ^& exit")
        os.chdir('..')

info_command = StreamInfo('GUI_{}'.format(mac), 'Event', 2, 0, 'string', 'id1234')
outlet_command = StreamOutlet(info_command)

streams_filename = resolve_byprop('name', 'Controller_{}'.format(mac))
inlet_filename = StreamInlet(streams_filename[0])  # ,max_buflen=1)

if bsr_cfg.user == 'master':
    ''' Outlet that Sends command and marker to the Slave '''
    info_stream2Slave = StreamInfo('CommandToSlave', 'Markers', 1, 0, 'string', 'myuidw43537')
    outlet_2Slave = StreamOutlet(info_stream2Slave)

if bsr_cfg.user == 'slave':
    ''' Inlet that receive commands and markers from the master'''
    stream_from_master = resolve_byprop('name', 'CommandToSlave')
    inlet_from_master = StreamInlet(stream_from_master[0])
    t_corr = inlet_from_master.time_correction()

if platform.system() == 'Windows':
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)
    screen_height = user32.GetSystemMetrics(1)

    # Config.set('graphics', 'borderless', 'true')

    # Config.set('modules', 'monitor', '')
    if bsr_cfg.fullscreen:
        Config.set('graphics', 'fullscreen', 'auto')
        
    else:
        if bsr_cfg.device == 'laptop':
            Config.set('graphics', 'width', str(screen_width))
            Config.set('graphics', 'height', str(screen_height - 30))
        elif bsr_cfg.device == 'tablet':
            Config.set('graphics', 'width', str(screen_width - 30))
            Config.set('graphics', 'height', str(screen_height))

Config.set('kivy', 'keyboard_mode', bsr_cfg.keyboard)

Config.set('graphics', 'window_state', 'minimized')
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('kivy', 'exit_on_escape', '0')

from kivy.app import App
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.modules import inspector
from kivy.logger import Logger
from kivy.core.window import Window

from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager,WipeTransition
from kivy.lang import Builder

from screens.home import Home
Builder.load_file('screens/home.kv')
from screens.bsr_settings import BSRSettings
Builder.load_file('screens/bsrsettings.kv')
from screens.signal_recorder import SignalRecorder
Builder.load_file('screens/signalrecorder.kv')

from screens.widgets.warning_popup import WarningPopup
from screens.widgets.confirm_popup import ConfirmPopup

images_folder = 'images'

def string2bool(string):
    if string == 'True':
        return True
    else:
        return False

class ErrorEmpaticaPopup(Popup):
    pass

class BSR_ScreenManager(ScreenManager):
    
    error_emp_popup = ObjectProperty()

    signal_recorder = ObjectProperty()
    bsr_settings = ObjectProperty()
    cfg_dict = {}

    # def __init__(self, **kwargs):

        # super(BSR_ScreenManager, self).__init__(**kwargs)
        # self.home = Home()
        # self.add_widget(self.home)

        # self.home.sr_btn.btn.bind(on_press = self.show_signal_recorder)
        # self.home.set_btn.btn.bind(on_press = self.show_bsr_settings)
        # self.current = 'home'
        # Window.minimize()

        # self.bsr_settings = BSRSettings(bsr_cfg,eeg_cfg,name='settings')
        # self.bsr_settings.read_settings_xml()
        # self.add_widget(self.bsr_settings)

        # self.signal_recorder = SignalRecorder(bsr_cfg,eeg_cfg,gsr_cfg,ppg_cfg,name='sr')
        # self.add_widget(self.signal_recorder)


        # if bsr_cfg.gsr_device == 'empatica' and not bsr_cfg.debug:
        #     self.empatica_evt = Clock.schedule_interval(self.listen_to_empatica, 1)
        #     self.founded_emp_err = False
        #     self.emp_warning_popup = None

        # if bsr_cfg.eeg_device == 'muse' and not bsr_cfg.debug:
        #     self.muse_evt = Clock.schedule_interval(self.listen_to_muse, 1)
        #     self.founded_muse_err = False
        #     self.muse_warning_popup = None

        # if bsr_cfg.user == 'slave':
        #     self.ts_command_master = local_clock()
        #     self.listen_event = Clock.schedule_interval(self.listen_to_master, 0.05)

        # self.contr_event = Clock.schedule_interval(self.check_controller, 5)
        
        # self.calibration_failed = False

        # self.founded_marker = False
        # self.marekr_event =  Clock.schedule_interval(self.listen_to_marker, 0.5)
        # # self.show_signal_recorder()
        # outlet_command2EEGapp.push_sample(["Start Acquisition"])
        # outlet_command2EEGapp.push_sample(["Check Impedances"])

       
    def show_bsr_settings(self,instance):
        self.current = 'settings'
        self.transition.direction = 'left'

    def close_settings(self):
        ok = self.bsr_settings.close_settings()
        if ok:
            self.current = 'home'
            self.transition.direction = 'right'

    def show_signal_recorder(self,instance):

        if not bsr_cfg.debug:
            if use_eeg:
                if bsr_cfg.eeg_device == 'liveAmp'or bsr_cfg.eeg_device == 'touch':
                    outlet_command2EEGapp.push_sample(["Start Acquisition"])
            if use_gsr:
                if bsr_cfg.gsr_device == 'shimmer':
                    outlet_commandToGsrApp.push_sample(["Start Acquisition"])

        acq_cfg = AcqConfig()
        info = vars(acq_cfg.info)
        proc = vars(acq_cfg.proc)
        acq_cfg_dict = {'info':info,'proc':proc,'met2compute':acq_cfg.met2compute}

        self.cfg_dict = {'bsr_cfg':vars(bsr_cfg),'eeg_cfg':vars(eeg_cfg),
                         'gsr_cfg':vars(gsr_cfg),'ppg_cfg':vars(ppg_cfg),
                         'acq_cfg':acq_cfg_dict}
        
        outlet_command.push_sample(["Start Acquisition",json.dumps(self.cfg_dict)])
        self.current = 'sr'
        self.transition.direction = 'left'

    def send_start(self):

        if self.signal_recorder.start_btn_image.source == os.path.join('images','start_icon_2.png'):
            if bsr_cfg.user == 'master':
                outlet_command.push_sample(["Start Recording","Bla"])
                outlet_command.push_sample([self.signal_recorder.task,"Bla"])
                outlet_2Slave.push_sample(["Start Recording"],timestamp=local_clock())

            elif bsr_cfg.user == 'slave':
                outlet_command.push_sample(["Start Recording","Bla"],timestamp=self.ts_command_master)
                outlet_command.push_sample([self.signal_recorder.task,"Bla"])
            self.signal_recorder.send_start()
        else:
            # if bsr_cfg.user == 'master':
            self.confirm_popup = ConfirmPopup(protocol='Classic')
            self.confirm_popup.bind(on_ok=self.stop_recording)
            self.confirm_popup.open()

    def stop_recording(self,obj):
        if bsr_cfg.user == 'master':
            outlet_command.push_sample(["Stop Recording","Bla"])
            outlet_2Slave.push_sample(["Stop Recording"],timestamp=local_clock())
        elif bsr_cfg.user == 'slave':
            outlet_command.push_sample(["Stop Recording","Bla"],timestamp=self.ts_command_master)

        self.signal_recorder.send_start()

    def send_marker(self):
        
        if bsr_cfg.user == 'master':
            outlet_command.push_sample(["Marker","Bla"])
            outlet_2Slave.push_sample(["Marker"],timestamp=local_clock())

        elif bsr_cfg.user == 'slave' and self.signal_recorder.marker_btn.state == 'down':
            outlet_command.push_sample(["Marker","Bla"],timestamp=local_clock())

        else:
            outlet_command.push_sample(["Marker","Bla"],timestamp=self.ts_command_master)
        
        self.signal_recorder.send_marker()

    def send_impedance_check(self):

        if not bsr_cfg.debug:
            if use_eeg:
                if bsr_cfg.eeg_device == 'liveAmp'or bsr_cfg.eeg_device == 'touch':
                    outlet_command2EEGapp.push_sample(["Check Impedances"])

        self.signal_recorder.send_impedance_check()

    def stop_impedance_check(self):

        if not bsr_cfg.debug:
            if use_eeg:
                if bsr_cfg.eeg_device == 'liveAmp'or bsr_cfg.eeg_device == 'touch':
                    outlet_command2EEGapp.push_sample(["Stop Check Impedances"])

        self.signal_recorder.stop_impedance_check()

    def save_impedances(self):
        
        self.signal_recorder.imp_popup.save_impedances()
        self.stop_impedance_check()

    def back_home_from_sr(self):
        self.signal_recorder.cancel_all_events()
        self.signal_recorder.close_all_streams()

        if not bsr_cfg.debug:
            if use_eeg:
                if bsr_cfg.eeg_device == 'liveAmp'or bsr_cfg.eeg_device == 'touch':
                    outlet_command2EEGapp.push_sample(["Stop Acquisition"])
            if use_gsr:
                if bsr_cfg.gsr_device == 'shimmer':
                    outlet_commandToGsrApp.push_sample(["Stop Acquisition"])

        self.current = 'home'
        self.transition.direction = 'right'
    
    def listen_to_marker(self, dt):
        if self.founded_marker:
            marker, timestamp_marker = self.inlet_marker.pull_sample(0.0)
            
            if marker is not None:
                Logger.info(marker)
                if str(marker[0]) == str("Marker"):
                    self.send_marker()     

        else:
            ''' Looking for the inlet'''
            self.marker_streams = resolve_byprop('name', 'bsr_marker', timeout=0.0)
            if self.marker_streams.__len__() != 0:
                self.inlet_marker = StreamInlet(self.marker_streams[0])
                self.founded_marker = True
                Logger.info("Founded marker stream")

    def listen_to_master(self, dt):

        master_cmd, timestamp_cmd = inlet_from_master.pull_sample(0.0)
        
        if master_cmd is not None:
            print(master_cmd)
            t_corr = inlet_from_master.time_correction()
            self.ts_command_master = timestamp_cmd  + t_corr

            if str(master_cmd[0]) == str("Start Recording"):
                self.send_start()
            if str(master_cmd[0]) == str("Stop Recording"):
                self.stop_recording('boh')
            if str(master_cmd[0]) == str("Marker"):
                self.send_marker()                    
            if str(master_cmd[0]) == str("Start NM Recording"):
                self.start_nm_recording()
            if str(master_cmd[0]) == str("Stop NM Recording"):
                self.stop_nm_recording('boh')
            if str(master_cmd[0]) == str("NM Marker"):
                self.send_nm_marker()

    def listen_to_empatica(self,dt):

        if self.founded_emp_err:
            sample_err, timestamp = self.inlet_em_err.pull_sample(timeout=0.0)

            if sample_err:
                print(sample_err[0])
                if 'connection lost to device' in sample_err[0]:
                    self.emp_warning_popup = WarningPopup(auto_dismiss=False)
                    self.emp_warning_popup.lab_txt = 'Empatica Disconnected. Wait for reconnection...'
                    self.emp_warning_popup.open()
                elif 'Starting BS Recorder' in sample_err[0]:
                    if self.emp_warning_popup:
                        self.emp_warning_popup.dismiss()

        else:
            ''' Looking for the inlet'''
            self.em_err_streams = resolve_byprop('name', 'ErrorStream{}'.format(gsr_cfg.serial), timeout=0.0)
            if self.em_err_streams.__len__() != 0:
                self.inlet_em_err = StreamInlet(self.em_err_streams[0])
                self.founded_emp_err = True

    def listen_to_muse(self,dt):

        if self.founded_muse_err:
            sample_err, timestamp = self.inlet_muse_err.pull_sample(timeout=0.0)

            if sample_err:
                print(sample_err[0])
                if 'Disconnected from' in sample_err[0]:
                    self.muse_warning_popup = WarningPopup(pos_hint={'x': 50.0 / Window.width,'y':50.0 /  Window.height},auto_dismiss=True)
                    self.muse_warning_popup.lab_txt = 'Muse Disconnected. Wait for reconnection...'
                    self.muse_warning_popup.open()
                if 'Successfully Connected' in sample_err[0]:
                    if self.muse_warning_popup:
                        self.muse_warning_popup.dismiss()
                if 'Not able to reconnect' in sample_err[0]:
                    self.muse_warning_popup = WarningPopup(pos_hint={'x': 50.0 / Window.width,'y':50.0 /  Window.height},auto_dismiss=True)
                    self.muse_warning_popup.lab_txt = 'Not able to reconnect to Muse. Restart the BSR.'
                    self.muse_warning_popup.open()

        else:
            ''' Looking for the inlet'''
            self.muse_err_streams = resolve_byprop('name', 'ErrorStream{}'.format(eeg_cfg.serial), timeout=0.0)
            if self.muse_err_streams.__len__() != 0:
                self.inlet_muse_err = StreamInlet(self.muse_err_streams[0])
                self.founded_muse_err = True

    def check_controller(self,dt):
        streams_filename = resolve_byprop('name', 'Controller_{}'.format(mac),timeout=0)
        
        if len(streams_filename) < 1:
            self.contr_warning_popup = WarningPopup(auto_dismiss=True)
            self.contr_warning_popup.lab_txt = 'Controller Disconnected. Restart the BSR'
            self.contr_warning_popup.open()
        
            self.contr_event.cancel()

    def close_app(self):
        if not bsr_cfg.debug:
            if use_eeg:
                # if bsr_cfg.eeg_device == 'liveAmp' or bsr_cfg.eeg_device == 'touch':
                outlet_command2EEGapp.push_sample(["Close Device"])

            if use_gsr:
                outlet_commandToGsrApp.push_sample(["Close Device"])
        else:
            outlet_commandToFakeApp.push_sample(["Close Device"])

        outlet_command.push_sample(["Close","Bla"])

        App.get_running_app().stop()

class BSRApp(MDApp):
    add_panel = True

    def __init__(self, **kwargs):
        super(BSRApp, self).__init__(**kwargs)
        Window.minimize()

    def build(self):
        def listen_to_websocket(self,message):
            print('Received: ' + message)
            if message == 'calibration' :
                outlet_command2EEGapp.push_sample(["Stop Acquisition"])
                # sleep(500)
                outlet_command2EEGapp.push_sample(["Check Impedances"])
            if message == 'acquisition' :
                outlet_command2EEGapp.push_sample(["Stop Check Impedances"])
                # sleep(500)
                outlet_command2EEGapp.push_sample(["Start Acquisition"])
        # Config.set('graphics', 'KIVY_CLOCK', 'interrupt')
        # self.theme_cls.theme_style = "Light"  # 
        # transition=WipeTransition()
        # transition.clearcolor=(0,0,0,0)
        # bsr = BSR_ScreenManager(transition = transition)
        # ws = create_connection("ws://127.0.0.1:8088/websocket/w")
        ws = websocket.WebSocketApp("ws://127.0.0.1:8888/websocket/w",
                                on_message=listen_to_websocket)


        
        outlet_command2EEGapp.push_sample(["Start Acquisition"])


        # outlet_command2EEGapp.push_sample(["Check Impedances"])
        self.use_kivy_settings = False
        print("finish !!!")
        ws.run_forever()
        return NULL
    
    

    # def on_stop(self):
        # self.profile.disable()
#         self.profile.dump_stats('BS_GUI.profile')


if __name__ == '__main__':
    
    if not os.path.exists("Data"):
        os.mkdir("Data")

    

    BSRApp().run()

    if not bsr_cfg.debug:
        if use_eeg:
            # if bsr_cfg.eeg_device == 'liveAmp' or bsr_cfg.eeg_device == 'touch':
            outlet_command2EEGapp.push_sample(["Close Device"])

        if use_gsr:
            # if bsr_cfg.gsr_device == 'shimmer':
            outlet_commandToGsrApp.push_sample(["Close Device"])
    else:
        outlet_commandToFakeApp.push_sample(["Close Device"])

    outlet_command.push_sample(["Close","Bla"])

