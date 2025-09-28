"""
Created on 13 lug 2017

@author: Anto
"""

from tkinter.tix import Tree
from pylsl import StreamInlet, resolve_stream, StreamOutlet, StreamInfo, resolve_byprop,local_clock

import time
from datetime import datetime
import os
import glob

from json.decoder import JSONDecoder
import json
import pickle

import numpy as np
import pandas as pd

from scipy.signal import lfilter,butter,lfilter_zi
import random
import sys
from utils.utils import create_filename,create_filename_online,compute_inlet_timeout

from collections import deque

from imblearn.over_sampling import ADASYN
from types import SimpleNamespace

from kivy.uix.boxlayout import BoxLayout
from kivy.logger import Logger

import psutil 
for interface in psutil.net_if_addrs():
    if psutil.net_if_addrs()[interface][0].address:
        mac = psutil.net_if_addrs()[interface][0].address
        break

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

''' Outlet that Sends info to the GUI '''
info_filename = StreamInfo('Controller_{}'.format(mac),'Event', 2,0,'string', source_id='id5678')
outlet_2GUI = StreamOutlet(info_filename)

''' Inlet that listen for User Commands'''
stream_command = resolve_byprop('name', 'GUI_{}'.format(mac))
inlet_command = StreamInlet(stream_command[0], max_buflen=1)
print("Resolved Gui stream")

# if bsr_cfg.user == 'master':
#     '''Sincro Sliders Stream'''
#     stream_slider_ID = random.randint(1, 2509403)
#     info_slider = StreamInfo('Sliders_Sincro', 'Event', 2, 0, 'string', 'slider1234')#str(stream_slider_ID))
#     outlet_slider = StreamOutlet(info_slider)


DELAY = 4
streams_eeg = None
inlet_eeg = None
streams_gsr = None
inlet_gsr = None
streams_ppg = None
inlet_ppg = None

while True:

    command, cmd_ts = inlet_command.pull_sample()

    if True:
        print(command[0])

        if True:
            cfg = SimpleNamespace(**json.loads(command[1]))
            bsr_cfg = SimpleNamespace(**cfg.bsr_cfg)
            eeg_cfg = SimpleNamespace(**cfg.eeg_cfg)
            gsr_cfg = SimpleNamespace(**cfg.gsr_cfg)
            ppg_cfg = SimpleNamespace(**cfg.ppg_cfg)
            acq_cfg = SimpleNamespace(**cfg.acq_cfg)
            info = SimpleNamespace(**acq_cfg.info)
            
            if not bsr_cfg.debug:
                if bsr_cfg.use_eeg:
                    NUM_EEG_CHANN = eeg_cfg.nr_chann
                    ch2compute = eeg_cfg.ch2compute
                    ch2compute_nr = eeg_cfg.ch2compute_nr #[ch[0] for ch in ch2compute]
                    EEG_CH = eeg_cfg.all_ch
                    FS_EEG = int(eeg_cfg.fs)
                    BS_EEG = int(eeg_cfg.bs)
                    EOG_CH = eeg_cfg.eog_ch[0]
                    fn = FS_EEG/2
                    filt_order = int(2*(DELAY*FS_EEG)+1)
                    BLOCK_RATE = int(FS_EEG/BS_EEG)
                    if not streams_eeg:
                        streams_eeg = resolve_byprop('name', '{}_EEG'.format(eeg_cfg.serial))
                        inlet_eeg = StreamInlet(streams_eeg[0])

                if bsr_cfg.use_gsr:
                    FS_GSR = gsr_cfg.fs_gsr
                    BS_GSR = gsr_cfg.bs_gsr
                    if not streams_gsr:
                        streams_gsr = resolve_stream('name', '{}_GSR'.format(gsr_cfg.serial))
                        inlet_gsr = StreamInlet(streams_gsr[0])


                if bsr_cfg.use_ppg:
                    FS_PPG = ppg_cfg.fs_ppg
                    BS_PPG = ppg_cfg.bs_ppg
                    if not streams_ppg:
                        streams_ppg = resolve_byprop('name', '{}_PPG'.format(ppg_cfg.serial))
                        if bsr_cfg.ppg_device == 'muse':
                            inlet_ppg = StreamInlet(streams_ppg[0],max_chunklen=6)
                        else:
                            inlet_ppg = StreamInlet(streams_ppg[0])

        # if str(command[0]) == str("Start Recording"):
        #     if not bsr_cfg.debug:

        #         id_sess_name = "{}{}".format(info.id, info.sess)

        #         inlet_timeout = compute_inlet_timeout(bsr_cfg)

        #         filename_2save = inlet_command.pull_sample(0.0)

        #         filename_eeg, filename_gsr, filename_ppg,filename_mrk = create_filename(id_sess_name,filename_2save[0][0],bsr_cfg)

        #         if bsr_cfg.use_eeg:
        #             eeg_sample, eeg_ts = inlet_eeg.pull_chunk(timeout=0.08)  # the first call to this takes a
        #             # bit more so we do that before entering the main loop
        #             while eeg_sample.__len__() > 0:
        #                 eeg_sample, eeg_ts = inlet_eeg.pull_chunk(timeout=0.0)  # the first call to this takes a

        #         if bsr_cfg.use_gsr:
        #             gsr_sample, gsr_ts = inlet_gsr.pull_chunk(0.0)  # to empty the buffer
        #             while gsr_sample.__len__() > 0:
        #                 gsr_sample, gsr_ts = inlet_gsr.pull_chunk(0.0)  # to empty the buffer

        #         if bsr_cfg.use_ppg:
        #             sample_ppg, ppg_ts = inlet_ppg.pull_chunk(0.0)  # to empty the buffer
        #             while sample_ppg.__len__() > 0:
        #                 sample_ppg, ppg_ts = inlet_ppg.pull_chunk(0.0)  # to empty the buffer

        #         f_mrk = open(filename_mrk, 'wb')
        #         header_mrk = ['Marker', 'MarkerTimestamp',datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]]
        #         np.savetxt(f_mrk, [], header='\t'.join(header_mrk), comments='')

        #         if bsr_cfg.use_eeg:
        #             f_eeg = open(filename_eeg, 'wb')
        #             header_eeg = ['Timestamp'] + EEG_CH 
        #             header_eeg.append(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
        #             header_eeg.append('fs={}'.format(FS_EEG))
        #             np.savetxt(f_eeg, [], header='\t'.join(header_eeg), comments='')

        #         if bsr_cfg.use_gsr:
        #             f_gsr = open(filename_gsr, 'wb')
        #             header_gsr = ['Timestamp', 'GSR',datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]]
        #             header_gsr.append('fs={}'.format(FS_GSR))
        #             np.savetxt(f_gsr, [], header='\t'.join(header_gsr), comments='')

        #         if bsr_cfg.use_ppg:
        #             f_ppg = open(filename_ppg, 'wb')
        #             header_ppg = ['Timestamp', 'PPG',datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]]
        #             header_ppg.append('fs={}'.format(FS_PPG))
        #             np.savetxt(f_ppg, [], header='\t'.join(header_ppg), comments='')

        #         stop_flag = False
        #         while not stop_flag:
        #             start_time = time.time()
        #             'EEG'
        #             if bsr_cfg.use_eeg:
        #                 eeg_sample, eeg_ts = inlet_eeg.pull_chunk(inlet_timeout['eeg'])
        #                 if eeg_sample.__len__():
        #                     np_eeg_sample = np.concatenate((np.resize(np.asarray(eeg_ts),
        #                                                             (np.asarray(eeg_ts).size, 1)),
        #                                                             np.asarray(eeg_sample)),1)
                            
        #                 if not f_eeg.closed:
        #                     if eeg_sample.__len__():
        #                         np.savetxt(f_eeg, np_eeg_sample, delimiter='\t', fmt='%.3f')
        #             'PPG'
        #             if bsr_cfg.use_ppg:
        #                 ppg_sample, ppg_ts = inlet_ppg.pull_chunk(inlet_timeout['ppg'])
        #                 if ppg_sample.__len__():
        #                     np_sample_ppg = np.concatenate((np.resize(np.asarray(ppg_ts), (np.asarray(ppg_ts).size, 1)),
        #                             np.asarray(ppg_sample)),1)
        #                 if not f_ppg.closed:
        #                     if ppg_sample.__len__():
        #                         np.savetxt(f_ppg, np_sample_ppg, delimiter='\t', fmt='%.3f')
        #             'GSR'
        #             if bsr_cfg.use_gsr:
        #                 gsr_sample, gsr_ts = inlet_gsr.pull_chunk(inlet_timeout['gsr'])
        #                 if gsr_sample.__len__():
        #                     np_gsr_sample = np.concatenate((np.resize(np.asarray(gsr_ts), (np.asarray(gsr_ts).size, 1)),
        #                             np.asarray(gsr_sample)),1)
        #                 if not f_gsr.closed:
        #                     if gsr_sample.__len__():
        #                         np.savetxt(f_gsr, np_gsr_sample, delimiter='\t', fmt='%.3f')
                                    
        #             command, cmd_ts = inlet_command.pull_sample(0.0)
        #             if command is not None:
        #                 if str(command[0]) == str("Stop Recording"):
        #                     stop_flag = True
        #                     f_mrk.close()
        #                     if bsr_cfg.use_eeg:
        #                         f_eeg.close()
        #                     if bsr_cfg.use_gsr:
        #                         f_gsr.close()
        #                     if bsr_cfg.use_ppg:
        #                         f_ppg.close()

        #                 if str(command[0]) == str("Marker"):
        #                     # if bsr_cfg.user == 'master':
        #                     #     'Slider Sincro'
        #                     #     outlet_slider.push_sample(["Marker", str(cmd_ts)])

        #                     if not f_mrk.closed:
        #                         mrk_2save = np.asarray([1,cmd_ts])
        #                         np.savetxt(f_mrk, np.resize(mrk_2save,(1,mrk_2save.size)), delimiter='\t', fmt='%.3f')

        if str(command[0]) == str("Close"):
            sys.exit()

