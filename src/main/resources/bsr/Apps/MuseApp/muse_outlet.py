import xml.etree.ElementTree as et
import os
from stream import stream

def string2bool(string):
    if string == 'True':
        return True
    else:
        return False


''' Connection Settings'''
et_amp = et.parse(os.path.join('config.cfg'))
sett_amp = et_amp.find('settings')
chan_amp = et_amp.find('channels')
labels_ch = chan_amp.find('labels')
        
muse_serial = sett_amp.find('deviceNumber').text

ppg_on = string2bool(sett_amp.find('ppg').text)

if ppg_on:
    stream(name=muse_serial,ppg_enabled=ppg_on,preset=51)
else:
    stream(name=muse_serial,preset=21)

