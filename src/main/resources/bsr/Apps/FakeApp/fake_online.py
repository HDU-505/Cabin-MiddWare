'''
Created on 10 dic 2018

@author: Antonio Di Florio
'''

import numpy as np
import os.path
import os
from pylsl import StreamInfo, StreamOutlet, local_clock, resolve_byprop, StreamInlet
import time, sys
import random 
import json
import xml.etree.ElementTree as et
from kivy.uix.boxlayout import BoxLayout

def string2bool(string):
    if string == 'True':
        return True
    else:
        return False

# et_amp = et.parse(os.path.join('config.cfg'))
# sett_amp = et_amp.find('settings')

use_eeg = True     
# use_eeg = string2bool(sett_amp.find('eeg').text)
# use_gsr = string2bool(sett_amp.find('gsr').text)
# use_ppg = string2bool(sett_amp.find('ppg').text)

block_rate = 10.0

if use_eeg:
    nan_ini_chunk = np.empty(30*int(block_rate),float)
    nan_ini_chunk.fill(np.nan)

else:
    nan_ini_chunk = np.empty(0*int(block_rate),float)
    nan_ini_chunk.fill(np.nan)

folder2load_fake = os.path.join("Data","online","EATS")
# folder2load_fake = os.path.join("Apps","FakeApp","Data","online","EATS")
list_of_data = os.listdir(folder2load_fake)
random.shuffle(list_of_data)

folder2load_fake_aw = os.path.join("Data","online")
# folder2load_fake_aw = os.path.join("Apps","FakeApp","Data","online")
aw_data_fake = np.loadtxt(os.path.join(folder2load_fake_aw,'AW_fake.dat'),skiprows=1)
aw = aw_data_fake[:,1]

met = ['workload','arousal']

neuro_data_fake_1 = np.loadtxt(os.path.join(folder2load_fake,list_of_data[0]),skiprows=1)
neuro_data_fake_2 = np.loadtxt(os.path.join(folder2load_fake,list_of_data[1]),skiprows=1)
neuro_data_fake_3 = np.loadtxt(os.path.join(folder2load_fake,list_of_data[2]),skiprows=1)
neuro_data_fake_4 = np.loadtxt(os.path.join(folder2load_fake,list_of_data[3]),skiprows=1)

neuro_data_fake_size_first = min(neuro_data_fake_1[:,0].size,neuro_data_fake_2[:,0].size)
neuro_data_fake_size_second = min(neuro_data_fake_3[:,0].size,neuro_data_fake_4[:,0].size)

neuro_data_fake_dict_first = {}
neuro_data_fake_dict_second = {}
last_good_value = {}
first_fake_value = {}
neuro_data_fake_dict = {}

ndx_met = 1
for m in met:
    neuro_data_fake_dict_first[m] = np.concatenate((nan_ini_chunk,(0.5*neuro_data_fake_1[0:neuro_data_fake_size_first,ndx_met]) + (0.5*neuro_data_fake_2[0:neuro_data_fake_size_first,ndx_met])))
    last_good_value[m] = neuro_data_fake_dict_first[m][-1]
    neuro_data_fake_dict_second[m] = (0.5*neuro_data_fake_3[0:neuro_data_fake_size_second,ndx_met]) + (0.5*neuro_data_fake_4[0:neuro_data_fake_size_second,ndx_met])
    # if m != 'arousal':
    first_fake_value[m] = neuro_data_fake_dict_second[m][0] #the first is always Nan
    # else:
    #     first_fake_value[m] = neuro_data_fake_dict_second[m][0]
    neuro_data_fake_dict_second[m] = neuro_data_fake_dict_second[m]+last_good_value[m]-first_fake_value[m]
    neuro_data_fake_dict[m] = np.concatenate((neuro_data_fake_dict_first[m],neuro_data_fake_dict_second[m]))

    ndx_met+=1

neuro_data_fake_dict_first['approachwithdrawal'] = np.concatenate((nan_ini_chunk,aw[0:neuro_data_fake_size_first]))
last_good_value['approachwithdrawal'] = neuro_data_fake_dict_first['approachwithdrawal'][neuro_data_fake_size_first-1]
neuro_data_fake_dict_second['approachwithdrawal'] = aw[0:neuro_data_fake_size_second]
first_fake_value['approachwithdrawal'] = neuro_data_fake_dict_second['approachwithdrawal'][1]
neuro_data_fake_dict_second['approachwithdrawal'] = neuro_data_fake_dict_second['approachwithdrawal']+last_good_value['approachwithdrawal']-first_fake_value['approachwithdrawal']
neuro_data_fake_dict['approachwithdrawal'] = np.concatenate((neuro_data_fake_dict_first['approachwithdrawal'],neuro_data_fake_dict_second['approachwithdrawal']))

neuro_data_fake_dict_size = neuro_data_fake_dict['workload'].size

print('resolving marker Stream')
mrk_streams = resolve_byprop('name', 'GUI_fake')
mrk_inlet = StreamInlet(mrk_streams[0])
print('resolved marker Stream')

info_neuro = StreamInfo('NM_fake', 'EEG', 1, 0, 'string', 'myuid34234')
outlet_neuro = StreamOutlet(info_neuro)

wait_for_start = mrk_inlet.pull_sample(0.1)

start_flag = False 

while not start_flag:
    wait_for_start,ts = mrk_inlet.pull_sample()
    if wait_for_start is not None:
        if str(wait_for_start[0]) == str("Start NM Recording Fake"):
            start_flag = True

print("started")

ndx = 0
 
ndx_block = 1

metrics = {}

while 1:
    
    cmd,ts = mrk_inlet.pull_sample(0.0)
    if ts:
        if cmd[0] == str("Stop NM Recording Fake"):                    
            sys.exit()

    if ndx == neuro_data_fake_dict_size-1:
        ndx =301
    
    metrics['workload'] = neuro_data_fake_dict['workload'][ndx]
    metrics['attention'] = neuro_data_fake_dict['workload'][ndx]
    metrics['arousal'] = neuro_data_fake_dict['arousal'][ndx]
    metrics['stress'] = neuro_data_fake_dict['arousal'][ndx]
    metrics['approachwithdrawal'] = neuro_data_fake_dict['approachwithdrawal'][ndx]
    metrics['ndx_block'] = ndx_block
    metrics['go_fake'] = False
         
    
    met_json = json.dumps(metrics)
     
    outlet_neuro.push_sample([met_json])
    
    ndx = ndx +1
    ndx_block = ndx_block+1
    
    time.sleep(1.0/block_rate)
