'''
Created on 07 set 2018

@author: Standard
'''

import sys, struct
import serial
import time
from pylsl import StreamInfo, StreamOutlet, local_clock,resolve_byprop,StreamInlet
import os
import xml.etree.ElementTree as et
import time
import serial.tools.list_ports

def Average(lst): 
    return sum(lst) / len(lst) 

def wait_for_ack():
    ddata = ""
    ack = struct.pack('B', 0xff)
    while ddata != ack:
        ddata = ser.read(1)
#         print "0x%02x" % ord(ddata[0])
    return

def string2bool(string):
    if string == 'True':
        return True
    else:
        return False

''' Connection Settings'''
tree = et.parse(os.path.join('config.cfg'))
gen = tree.find('general')

shimmer_serial = gen.find('serial').text
shimmer_fs = float(gen.find('fs_gsr').text)
shimmer_bs = float(gen.find('bs_gsr').text)
ppg_on = string2bool(gen.find('ppg').text)

print("Resolving Command Stream...")
streams_command = resolve_byprop('name', 'CommandFromGui_{}'.format(shimmer_serial))
inlet_command = StreamInlet(streams_command[0])
print("Found Command Stream!")

info_error = StreamInfo('ErrorStream{}'.format(shimmer_serial), 'Markers', 1, 0, 'string', 'myuidw43536')
outlet_error = StreamOutlet(info_error)

time.sleep(0.5)

ports = list(serial.tools.list_ports.comports())
com_port = None
for p in ports:
    if shimmer_serial in p.hwid:
        com_port = p.device #,p.hwid[-14:-10])
if not com_port:
    print("Device not found, pair the device first")
    outlet_error.push_sample(["Shimmer Not Connected"])
else:
    try:
        print("Connecting to Shimmer {}".format(shimmer_serial))
        outlet_error.push_sample(["Connecting to Shimmer {}...".format(shimmer_serial)])
        ser = serial.Serial(com_port, 115200)
        ser.flushInput()
        print("Connected")
        if ppg_on:
            outlet_error.push_sample(["Activating GSR and PPG sensors..."])
        else:
            outlet_error.push_sample(["Activating GSR sensor..."])
    except:
        print("Excepting")
        outlet_error.push_sample(["Shimmer Not Connected"])
        time.sleep(0.5)
        outlet_error.__del__()
    else:
        time.sleep(0.5)
        try:
            # send the set sensors command
            if ppg_on:
                ser.write(struct.pack('BBBB', 0x08, 0x04, 0x21, 0x00))  #ppg (Int13)
            else:
                ser.write(struct.pack('BBBB', 0x08, 0x04, 0x20, 0x00))
                
            wait_for_ack()
            outlet_error.push_sample(["Setting the sampling rate to {} Hz...".format(shimmer_fs)])
            print("Sensors Activated")
        except:
            outlet_error.push_sample(["Problem activating sensors"])
        else:
            time.sleep(0.5)
            try:
                # send the set sampling rate command
                #51.2Hz (32768/640=51.2Hz: 640 -> 0x0280; has to be done like this for alignment reasons.)
                #102.4Hz -> 320 -> 0x0140
                #128 Hz -> 256 -> 0x0100
                # 64 Hz -> 512 -> 0x0200
                if shimmer_fs == 51.2:
                    ser.write(struct.pack('BBB', 0x05, 0x80, 0x02))
                elif  shimmer_fs == 64.0:
                    ser.write(struct.pack('BBB', 0x05, 0x00, 0x02))
                elif  shimmer_fs == 102.4:
                    ser.write(struct.pack('BBB', 0x05, 0x40, 0x01))
                elif  shimmer_fs == 128.0:
                    ser.write(struct.pack('BBB', 0x05, 0x00, 0x01))
                
                wait_for_ack()                                  
                print("Sampling Rate Set to {} Hz".format(shimmer_fs))
                outlet_error.push_sample(["Starting BS Recorder..."])
            except:
                outlet_error.push_sample(["Problem setting the Sampling Rate"])
            else:
                time.sleep(0.5)
                info_gsr = StreamInfo('{}_GSR'.format(shimmer_serial), 'GSR', 1, shimmer_fs, 'float32', 'myuid2424')
                outlet_gsr = StreamOutlet(info_gsr)
                info_batt = StreamInfo('{}_GSR_Battery'.format(shimmer_serial), 'Marker', 1, shimmer_fs, 'float32', 'myuidblabla')
                outlet_batt = StreamOutlet(info_batt)
                if ppg_on:
                    info_ppg = StreamInfo('{}_PPG'.format(shimmer_serial), 'PPG', 1, shimmer_fs, 'float32', 'myuid2425')
                    outlet_ppg = StreamOutlet(info_ppg)
                
                # read incoming data
                ddata = bytearray()
                numbytes = 0
                if ppg_on:
                    framesize = 10 # 1byte packet type + 3byte timestamp + 2byte Battery + 2byte GSR + 2 PPG
                else:
                    framesize = 8 # 1byte packet type + 3byte timestamp +  2byte Battery + 2byte GSR
                
                frame_packet = int(framesize)
                
                s = time.time()
                
                while True:

                    cmd,ts = inlet_command.pull_sample()

                    if ts:
                        if cmd[0] == str("Start Acquisition"):
                            try:       
                                # send start streaming command
                                ser.write(struct.pack('B', 0x07))
                                wait_for_ack()
                                print("Streaming...")
                            except:
                                print("Problem sending the start streaming command")
                            else:
                                stop_flag = False
                                while not stop_flag:

                                    while numbytes < frame_packet:
                                        ddata += ser.read(frame_packet)
                                        numbytes = len(ddata)
                                        
                                    data = ddata[0:frame_packet]
                                    ddata = ddata[frame_packet:]
                                    numbytes = len(ddata)
                                
                                    out_packet = []

                                    if ppg_on:
                                        (raw_batt,raw_ppg,raw_gsr) = struct.unpack('HHH', data[4:framesize])
                                    else:
                                        (raw_batt,raw_gsr) = struct.unpack('HH', data[4:framesize])

                                    # get current GSR range resistor value  
                                    Range = ((raw_gsr >> 14) & 0xff)  # upper two bits
                                    if(Range == 0):
                                        Rf = 40.2   # kohm
                                    elif(Range == 1):
                                        Rf = 287.0  # kohm
                                    elif(Range == 2):
                                        Rf = 1000.0 # kohm
                                    elif(Range == 3):
                                        Rf = 3300.0 # kohm

                                    # convert GSR to kohm value
                                    gsr_to_volts = (raw_gsr & 0x3fff) * (3.0/4095.0)
                                    GSR_ohm = Rf/( (gsr_to_volts /0.5) - 1.0)
                                    sample_gsr = (1/GSR_ohm)*1000

                                    outlet_gsr.push_sample([sample_gsr])

                                    if time.time()-s > 10:
                                        batt = raw_batt* (3000.0/4095.0)*2
                                        outlet_batt.push_sample([batt])
                                        s= time.time()

                                    if ppg_on:
                                        PPG_mv = raw_ppg * (3000.0/4095.0)
                                        outlet_ppg.push_sample([PPG_mv])

                                    cmd, cmd_ts = inlet_command.pull_sample(0.0)
                                    if cmd_ts:

                                        if str(cmd[0]) == str("Stop Acquisition"):
                                            stop_flag = True 
                                            #send stop streaming command
                                            ser.write(struct.pack('B', 0x20))
                                            wait_for_ack()
                                            print("stop command sent, waiting for ACK_COMMAND")
                        
                        if cmd[0] == str("Close Device"):                    
                            #close serial port
                            ser.close()
                            print("All done")
                            sys.exit()