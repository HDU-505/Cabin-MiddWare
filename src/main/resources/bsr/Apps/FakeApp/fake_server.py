'''
Created on 04 dic 2018

@author: Antonio Di Florio
'''

import numpy as np
import os.path
from pylsl import StreamInfo, StreamOutlet, local_clock, resolve_byprop,StreamInlet
import time,sys
import xml.etree.ElementTree as et

def string2bool(string):
    if string == 'True':
        return True
    else:
        return False

print("Resolving Command Stream...")
streams_command = resolve_byprop('name', 'CommandFromGui_fake')
inlet_command = StreamInlet(streams_command[0])
print("Found Command Stream!")

folder2load = os.path.join("Data","scope")
run2load = 'EyesOpen'

et_amp = et.parse(os.path.join('config.cfg'))
sett_amp = et_amp.find('settings')
        
use_eeg = string2bool(sett_amp.find('eeg').text)
eeg_dev = sett_amp.find('eeg_dev').text

if eeg_dev == 'liveAmp':
    FS_EEG = 250
    BS_EEG = 25
    block_size_gsr = 10.0
    block_size_ppg = 10.0
elif eeg_dev == 'touch':
    FS_EEG = 125
    BS_EEG = 25
    block_size_gsr = 20.0
    block_size_ppg = 20.0
elif eeg_dev == 'muse':
    FS_EEG = 256
    BS_EEG = 32
    block_size_gsr = 10.0
    block_size_ppg = 10.0

block_size_eeg = float(BS_EEG)

use_gsr = string2bool(sett_amp.find('gsr').text)
use_ppg = string2bool(sett_amp.find('ppg').text)

NUM_CHANN = int(sett_amp.find('channelcount').text)

if use_eeg:
    
    info_eeg = StreamInfo('fake_EEG', 'EEG', NUM_CHANN, FS_EEG, 'float32', 'myuid34234')
    outlet_eeg = StreamOutlet(info_eeg,BS_EEG,360)
    
    eeg2load = '{}_eeg.dat'.format(run2load)
    eeg_data = np.loadtxt(os.path.join(folder2load,eeg2load),skiprows=1)
    eeg = eeg_data[:,1:NUM_CHANN+1] #/ EEG_AMP * EEG_RES

gsr2load = '{}_gsr.dat'.format(run2load)
gsr_data = np.loadtxt(os.path.join(folder2load,gsr2load),skiprows=1)

if use_gsr:
    info_gsr = StreamInfo('fake_GSR', 'GSR', 1, 100, 'float32', 'myuid2424')
    outlet_gsr = StreamOutlet(info_gsr,int(block_size_gsr),360)
    gsr = gsr_data[:,1]

if use_ppg:
    info_ppg = StreamInfo('fake_PPG', 'PPG', 1, 100, 'float32', 'myuid2424')
    outlet_ppg = StreamOutlet(info_ppg,int(block_size_ppg),360)
    ppg = gsr_data[:,2]


ndx_block = 0

if use_gsr:
    end = gsr.size
elif use_ppg:
    end = ppg.size
else:
    end = eeg[:,0].size

while 1:

    cmd,ts = inlet_command.pull_sample(0.0)
    if ts:
        if cmd[0] == str("Close Device"):                    
            sys.exit()

    if use_eeg:
        eeg_block = eeg[ndx_block*int(block_size_eeg):(ndx_block+1)*int(block_size_eeg),:]
        outlet_eeg.push_chunk(eeg_block.tolist())
    if use_gsr:
        gsr_block = gsr[ndx_block*int(block_size_gsr):(ndx_block+1)*int(block_size_gsr)]
        outlet_gsr.push_chunk(gsr_block.tolist())
    if use_ppg:
        ppg_block = ppg[ndx_block*int(block_size_ppg):(ndx_block+1)*int(block_size_ppg)]
        outlet_ppg.push_chunk(ppg_block.tolist())

    ndx_block += 1
    
    if ndx_block*block_size_eeg > end:
        ndx_block = 0
    
    time.sleep(float(BS_EEG/FS_EEG))    
