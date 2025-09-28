

'''
Created on 23 nov 2018

@author: Standard
'''

import os

from pylsl import StreamInlet,resolve_byprop

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.config import Config
Config.set('graphics', 'fullscreen', 0)
Config.set('graphics', 'resizable', 'False')
Config.set('graphics', 'width', '476')
Config.set('graphics', 'height', '153')
Config.set('graphics', 'borderless', 1)

from kivy.modules import inspector
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty,StringProperty


from utils.settings_class import BSRConfig,EEGConfig,GSRConfig,PPGConfig

''' Connection Settings'''
bsr_cfg = BSRConfig("start_config.xml")
if bsr_cfg.use_eeg:
    eeg_cfg = EEGConfig(bsr_cfg.eeg_device)
if bsr_cfg.use_gsr:
    gsr_cfg = GSRConfig(bsr_cfg.gsr_device)
if bsr_cfg.use_ppg:
    ppg_cfg = PPGConfig(bsr_cfg.ppg_device)

use_eeg = bsr_cfg.use_eeg
use_gsr = bsr_cfg.use_gsr
use_ppg = bsr_cfg.use_ppg

if use_eeg:
    eeg_device = bsr_cfg.eeg_device
    eeg_device_serial = eeg_cfg.serial
if use_gsr:
    gsr_device = bsr_cfg.gsr_device
    gsr_device_serial = gsr_cfg.serial


class Home(BoxLayout):
    
    if use_eeg:
        if eeg_device == 'liveAmp' or eeg_device == 'touch':
            error_lab = StringProperty("正在连接 {} {}...".format(eeg_device,eeg_device_serial))
        elif eeg_device == 'muse':
            error_lab = StringProperty('正在寻找 {}, 这可能会需要 10s ...'.format(eeg_device_serial))
    elif use_gsr:
        error_lab = StringProperty("Connecting to {} {}...".format(gsr_device,gsr_device_serial))

    error_popup = ObjectProperty()
    
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        # Window.minimize()
        
        self.founded_la = False
        self.founded_muse = False
        self.founded_sh = False
        self.founded_em = False
        
        if not bsr_cfg.debug:
            if use_eeg:
                if eeg_device == 'liveAmp'or eeg_device == 'touch':
                    self.upd_event_la = Clock.schedule_interval(self.update_liveAmp,0.2) 
                    os.chdir("Batch")       
                    os.system("start /min startEegAmpApp.bat ^& exit")
                    os.chdir("..")
                elif eeg_device == 'muse':
                    self.upd_event_muse = Clock.schedule_interval(self.update_muse,0.2) 
                    os.chdir("Batch")       
                    os.system("start /min startMuseApp.bat ^& exit")
                    os.chdir("..")
            else:
                if use_gsr and gsr_device == 'empatica':
                    os.chdir("Batch")
                    os.system("start /min startEmpaticaApp.bat ^& exit")
                    os.chdir("..")
                    self.upd_em_event = Clock.schedule_interval(self.update_empatica,0.1)
                elif use_gsr and gsr_device == 'shimmer':
                    os.chdir("Batch")            
                    os.system("start /min startShimmerApp.bat ^& exit")
                    os.chdir("..")
                    self.upd_sh_event = Clock.schedule_interval(self.update_shimmer,0.2)
        else:
            self.upd_event_fake = Clock.schedule_once(self.update_fake,3)
            
    def update_liveAmp(self,dt):
        
        if not self.founded_la:        
            ''' Looking for the inlet'''
            self.error_streams = resolve_byprop('name', 'error{}'.format(eeg_device_serial),timeout=0.0)
            if self.error_streams.__len__() != 0:
                self.inlet_error = StreamInlet(self.error_streams[0])
                self.founded_la = True
        else:
            err = self.inlet_error.pull_sample(timeout=0.0)
            if err[0] is not None:
                self.error_lab = str(err[0][0])
                print(err[0][0])
                if self.error_lab == "Succesfully connected to {}{}.".format(eeg_device,eeg_device_serial):
                    if use_gsr and gsr_device == 'shimmer':
                        os.chdir("Batch") 
                        os.system("start /min startShimmerApp.bat ^& exit")
                        os.chdir("..")
                        self.upd_sh_event = Clock.schedule_interval(self.update_shimmer,0.2)
                    elif use_gsr and gsr_device == 'empatica':
                        os.chdir("Batch")
                        os.system("start /min startEmpaticaApp.bat ^& exit")
                        os.chdir("..")
                        self.upd_em_event = Clock.schedule_interval(self.update_empatica,0.1)
                    elif not use_gsr:
                        os.chdir("Batch")       
                        os.system("start /min startBsr.bat ^& exit")
                        os.chdir("..")

                        self.error_lab = '正在启动 NeuroX ...'
                        Clock.schedule_once(self.close, 5)
                    self.upd_event_la.cancel()
                    
                if self.error_lab == "No Amplifier connected or device wasn't properly closed.":
                    self.error_popup = ErrorPopup_LA()
                    # self.error_popup.bind(on_ok=self.restart_la)
                    Clock.schedule_once(self.restart_la,3)
                    self.error_popup.open()
                    self.inlet_error.close_stream()
                    self.upd_event_la.cancel()

    
    def update_muse(self,dt):

        if not self.founded_muse:        
            ''' Looking for the inlet'''
            self.error_streams = resolve_byprop('name', 'ErrorStream{}'.format(eeg_device_serial),timeout=0.0)
            if self.error_streams.__len__() != 0:
                self.inlet_error = StreamInlet(self.error_streams[0])
                self.founded_muse = True
            
        else:
            err = self.inlet_error.pull_sample(timeout=0.0)
            if err[0] is not None:
                self.error_lab = str(err[0][0])
                print(err[0][0])
                if self.error_lab == "Successfully Connected with {}".format(eeg_device_serial):
                    # if use_gsr and gsr_device == 'shimmer':
                    #     os.chdir("Batch") 
                    #     os.system("start /min startShimmerApp.bat ^& exit")
                    #     os.chdir("..")
                    #     self.upd_sh_event = Clock.schedule_interval(self.update_shimmer,0.2)
                    # elif use_gsr and gsr_device == 'empatica':
                    #     os.chdir("Batch")
                    #     os.system("start /min startEmpaticaApp.bat ^& exit")
                    #     os.chdir("..")
                    #     self.upd_em_event = Clock.schedule_interval(self.update_empatica,0.1)
                    # elif not use_gsr:
                    #     os.chdir("Batch")       
                    #     os.system("start /min startBsr.bat ^& exit")
                    #     os.chdir("..")

                        self.error_lab = '正在启动 NeuroX ...'
                        Clock.schedule_once(self.close, 3)
                    # self.upd_event_muse.cancel()

                # if self.error_lab == "No Muse found.":                    
                #     self.error_popup = ErrorPopup_Muse()
                #     self.error_popup.bind(on_ok=self.restart_muse)
                #     self.error_popup.open()
                #     self.inlet_error.close_stream()
                #     self.upd_event_muse.cancel()

    def update_fake(self,dt):
        if use_eeg:
            self.error_lab = "Succesfully connected to {} {}...".format(eeg_device,eeg_device_serial)
            if use_gsr:
                self.upd_event_fake_1 = Clock.schedule_once(self.update_fake_1,1.5)
            else:
                self.upd_event_fake_2 = Clock.schedule_once(self.update_fake_2,1.5)
        else:
            self.upd_event_fake_1 = Clock.schedule_once(self.update_fake_1,-1)

    def update_fake_1(self,dt):
        # if gsr_device == 'shimmer':
        #     self.error_lab = "Connecting to Shimmer {}...".format(gsr_device_serial)
        # else:
        #     self.error_lab = "Connecting to Empatica {}...".format(gsr_device_serial)
            
        self.upd_event_fake_2 = Clock.schedule_once(self.update_fake_2,1.5)
    
    def update_fake_2(self,dt):
        os.chdir("Batch")       
        os.system("start /min startBsr.bat ^& exit")
        os.chdir("..")

        self.error_lab = "正在启动 NeuroX ..."
        self.close_fake_event = Clock.schedule_once(self.close_fake,4)
    
    def close_fake(self,dt):
        App.get_running_app().stop()
               
    # def update_shimmer(self,dt):
        
    #     if not self.founded_sh:        
    #         ''' Looking for the inlet'''
    #         self.error_streams_sh = resolve_byprop('name', 'ErrorStream{}'.format(gsr_device_serial),timeout=0.0)
    #         if self.error_streams_sh.__len__() != 0:
    #             self.inlet_error_sh = StreamInlet(self.error_streams_sh[0])
    #             self.founded_sh = True
    #     else:
    #         err = self.inlet_error_sh.pull_sample(timeout=0.0)
            
    #         if err[0] is not None:
    #             print(err[0])

    #             self.error_lab = str(err[0][0])
    #             if self.error_lab == 'Starting BS Recorder...':
    #                 os.chdir("Batch")       
    #                 os.system("start /min startBsr.bat ^& exit")
    #                 os.chdir("..")

    #                 Clock.schedule_once(self.close, 5)
                    
    #             if self.error_lab == "Shimmer Not Connected":
    #                 self.inlet_error_sh.close_stream()
    #                 self.upd_sh_event.cancel()
    #                 self.error_popup = ErrorPopup_SH()
    #                 self.error_popup.ok_btn.bind(on_press = self.restart_sh)
    #                 self.error_popup.open()
    
    # def update_empatica(self,dt):
        
    #     if not self.founded_em:        
    #         ''' Looking for the inlet'''
    #         self.error_streams_em = resolve_byprop('name', 'ErrorStream{}'.format(gsr_device_serial),timeout=0.0)
    #         if self.error_streams_em.__len__() != 0:
    #             self.inlet_error_em = StreamInlet(self.error_streams_em[0])
    #             self.founded_em = True
    #     else:
    #         err = self.inlet_error_em.pull_sample(timeout=0.0)
            
    #         if err[0] is not None:
    #             self.error_lab = str(err[0][0])
    #             if self.error_lab == 'Starting BS Recorder...':
    #                 os.chdir("Batch")       
    #                 os.system("start /min startBsr.bat ^& exit")
    #                 os.chdir("..")

    #                 Clock.schedule_once(self.close, 5)

    def close(self,dt):
        
        if use_gsr:
            if gsr_device == 'shimmer': 
                self.upd_sh_event.cancel()
            elif gsr_device == 'empatica':
                self.upd_em_event.cancel()
            
        App.get_running_app().stop()
        
    def restart_la(self,obj):
        
        self.error_lab = "Pairing with {} {}...".format(eeg_device,eeg_device_serial)
        self.founded_la = False
        os.chdir("Batch")
        os.system("start /min startEegAmpApp.bat ^& exit")
        os.chdir("..")
        self.upd_event_la = Clock.schedule_interval(self.update_liveAmp,0.01)

    # def restart_muse(self,obj):
        
    #     self.error_lab = "Pairing with {}...".format(eeg_device_serial)
    #     self.founded_muse = False
    #     os.chdir("Batch")
    #     os.system("start /min startMuseApp.bat ^& exit")
    #     os.chdir("..")
    #     self.upd_event_la = Clock.schedule_interval(self.update_muse,0.01)

    # def restart_sh(self,obj):
        
    #     print('restarting')
    #     self.error_popup.ok_btn.disabled = True
    #     self.error_popup.dismiss()
    #     self.error_lab = "Connecting to Shimmer {}...".format(gsr_device_serial)
    #     self.founded_sh = False
    #     os.chdir("Batch")
    #     os.system("start /min startShimmerApp.bat ^& exit")
    #     os.chdir("..")
    #     self.upd_sh_event = Clock.schedule_interval(self.update_shimmer,0.2)

# class ErrorPopup_SH(Popup):
    
#     text = StringProperty('')    
#     ok_text = StringProperty('OK')
#     instructions = StringProperty('')
#     ok_btn = ObjectProperty()

#     # __events__ = ('on_ok', 'on_cancel')

#     def __init__(self,**kwargs):
        
#         super(ErrorPopup_SH, self).__init__(**kwargs)
#         self.background = "images/blu_back.png" 
#         self.instructions = 'Power Off/On the device and press OK \nIf the error persist check the configuration file'  
    
#     # def ok(self):
#     #     self.dispatch('on_ok')
#     #     self.dismiss()
    
#     # def on_ok(self):
#     #     self.dismiss()
    
#     # def on_cancel(self):
#     #     pass

class ErrorPopup_LA(Popup):
    
    text = StringProperty('')    
    ok_text = StringProperty('确认')
    instructions = StringProperty('')
    
    __events__ = ('on_ok', 'on_cancel')

    def __init__(self,**kwargs):
        
        super(ErrorPopup_LA, self).__init__(**kwargs)
        self.background = "images/blu_back.png" 
        self.instructions = '请启动/重启设备并按确认键 \n如果错误仍然存在请检查配置文件'  
    
    def ok(self):
        self.dispatch('on_ok')
        self.dismiss()
    
    def on_ok(self):
        pass
    
    def on_cancel(self):
        pass

# class ErrorPopup_Muse(Popup):
    
#     text = StringProperty('')    
#     ok_text = StringProperty('OK')
#     instructions = StringProperty('')
    
#     __events__ = ('on_ok', 'on_cancel')

#     def __init__(self,**kwargs):
        
#         super(ErrorPopup_Muse, self).__init__(**kwargs)
#         self.background = "images/blu_back.png" 
#         self.instructions = 'Power Off/On the device and press OK \nIf the error persist check the configuration file'  
    
#     def ok(self):
#         self.dispatch('on_ok')
#         self.dismiss()
    
#     def on_ok(self):
#         pass
    
#     def on_cancel(self):
#         pass

class STARTUPApp(App):

    pass

if __name__ == "__main__":
    STARTUPApp().run() 