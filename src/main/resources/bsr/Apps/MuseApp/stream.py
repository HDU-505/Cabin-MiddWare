from asyncio import CancelledError
from sys import platform
from time import time
from functools import partial

from pylsl import StreamInfo, StreamOutlet,local_clock, resolve_byprop, StreamInlet
import xml.etree.ElementTree as et
import os

''' Connection Settings'''
et_amp = et.parse(os.path.join('config.cfg'))
sett_amp = et_amp.find('settings')        
muse_serial = sett_amp.find('deviceNumber').text

import backends
from bleak.exc import BleakError
import sys

from muse import Muse
from constants import MUSE_SCAN_TIMEOUT, AUTO_DISCONNECT_DELAY,  \
    MUSE_NB_EEG_CHANNELS, MUSE_SAMPLING_EEG_RATE, LSL_EEG_CHUNK,  \
    MUSE_NB_PPG_CHANNELS, MUSE_SAMPLING_PPG_RATE, LSL_PPG_CHUNK

info_error = StreamInfo('ErrorStream{}'.format(muse_serial), 'Markers', 1, 0, 'string', 'myuidw43536')
outlet_error = StreamOutlet(info_error)

print("Resolving Command Stream...")
streams_command = resolve_byprop('name', 'CommandFromGui_{}'.format(muse_serial))
inlet_command = StreamInlet(streams_command[0])
print("Found Command Stream!")

# Returns the address of the Muse with the name provided, otherwise returns address of first available Muse.
def find_muse(name=None,timeout=MUSE_SCAN_TIMEOUT):

    # Returns a list of available Muse devices.
    adapter = backends.BleakBackend()
    adapter.start()
    print('Searching for Muses, this may take up to 10 seconds...')
    devices = adapter.scan(timeout=timeout)
    adapter.stop()

    muses = [d for d in devices if d['name'] and 'Muse' in d['name']]

    correct_muse_founded = False

    for m in muses:
        print(f'Found device {m["name"]}, MAC Address {m["address"]}')
        if m['name'] == name:
            outlet_error.push_sample([f'Found device {m["name"]}, MAC Address {m["address"]}'])
            correct_muse_founded = True

    if not muses or not correct_muse_founded:
        print('No Muse found.')
        outlet_error.push_sample(['No Muse found.'])
        return

    if name:
        for muse in muses:
            if muse['name'] == name:
                return muse
    elif muses:
        return muses[0]


# Begins LSL stream(s) from a Muse with a given address with data sources determined by arguments
def stream(name=None,ppg_enabled=False,eeg_disabled=False,preset=None,timeout=AUTO_DISCONNECT_DELAY):
    
    # If no data types are enabled, we warn the user and return immediately.
    if eeg_disabled and not ppg_enabled:
        print('Stream initiation failed: At least one data source must be enabled.')
        return

    found_muse = find_muse(name)
    if not found_muse:
        return
    else:
        address = found_muse['address']
        name = found_muse['name']

    if not eeg_disabled:
        eeg_info = StreamInfo('{}_EEG'.format(name), 'EEG', MUSE_NB_EEG_CHANNELS-1, MUSE_SAMPLING_EEG_RATE, 'float32',
                            'Muse%s' % address)
        eeg_outlet = StreamOutlet(eeg_info)#, LSL_EEG_CHUNK)


    batt_info = StreamInfo('{}_EEG_Battery'.format(name), 'Marker', 1, 0, 'float32',
                        'Muse%s' % address)
    batt_outlet = StreamOutlet(batt_info)

    if ppg_enabled:
        ppg_info = StreamInfo('{}_PPG'.format(name), 'PPG', MUSE_NB_PPG_CHANNELS-2, MUSE_SAMPLING_PPG_RATE,
                            'float32', 'Muse%s' % address)
        ppg_outlet = StreamOutlet(ppg_info, LSL_PPG_CHUNK)


    def push(data, timestamps, outlet):
        for ii in range(data.shape[1]):
            outlet.push_sample(data[:, ii], timestamps[ii])

    push_eeg = partial(push, outlet=eeg_outlet) if not eeg_disabled else None
    push_batt = partial(push,outlet=batt_outlet)
    push_ppg = partial(push, outlet=ppg_outlet) if ppg_enabled else None

    muse = Muse(address=address, callback_eeg=push_eeg, callback_ppg=push_ppg,name=name, preset=preset,callback_telemetry=push_batt)

    didConnect = muse.connect()

    if(didConnect):
        print('Connected.')
        outlet_error.push_sample(['Successfully Connected with {}'.format(muse_serial)])
        muse.start()

        eeg_string = " EEG" if not eeg_disabled else ""
        ppg_string = " PPG" if ppg_enabled else ""

        print("Streaming%s%s..." %(eeg_string, ppg_string))

        while True: 

            cmd, cmd_ts = inlet_command.pull_sample(0.0)
            if cmd_ts:
                if str(cmd[0]) == str("Close Device"):
                    muse.disconnect()
                    print('Disconnected.')
                    backends.sleep(5)
                    sys.exit()

            if local_clock() - muse.last_timestamp < timeout:
                backends.sleep(1)
            else:
                outlet_error.push_sample(['Disconnected from {}'.format(muse_serial)])
                muse.disconnect()
                print('Disconnected.')
                backends.sleep(5)
                try:
                    didConnect = muse.connect()
                except BleakError:
                    found_muse = find_muse(name,30)
                    if not found_muse:
                        return
                    else:
                        address = found_muse['address']
                        name = found_muse['name']
                    muse = Muse(address=address, callback_eeg=push_eeg, callback_ppg=push_ppg,name=name, preset=preset,callback_telemetry=push_batt)
                    didConnect = muse.connect()
                except CancelledError:
                    outlet_error.push_sample(['Not able to reconnect to {}'.format(muse_serial)])
                    backends.sleep(5)
                    sys.exit()    
                finally:
                    outlet_error.push_sample(['Successfully Connected with {}'.format(muse_serial)])
                    print('Connected.')
                    muse.start()
                    print("Streaming%s%s..." %(eeg_string, ppg_string))

        

