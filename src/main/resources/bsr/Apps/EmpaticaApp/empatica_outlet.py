import time
import socket                                                                                                                                
import os
from pylsl import StreamInfo, StreamOutlet,resolve_stream,StreamInlet
import xml.etree.ElementTree as et
import sys

TCP_IP = '127.0.0.1'
TCP_PORT = 28000
BUFF_SIZE = 4096

FS_GSR = 4
FS_PPG = 64

def string2bool(string):
    if string == 'True':
        return True
    else:
        return False

''' Connection Settings'''
tree = et.parse(os.path.join("config.cfg"))
gen = tree.find('general')

empatica_serial = gen.find('serial').text
ppg_on = string2bool(gen.find('ppg').text)
gui = string2bool(gen.find('gui').text)

info_error = StreamInfo('ErrorStream{}'.format(empatica_serial), 'Markers', 1, 0, 'string', 'myuidw43536')
outlet_error = StreamOutlet(info_error)


print("Resolving Command Stream...")
streams_command = resolve_stream('name', 'CommandFromGui_{}'.format(empatica_serial))
inlet_command = StreamInlet(streams_command[0])
print("Found Command Stream!")

outlet_error.push_sample(["Connecting to Empatica {}...".format(empatica_serial)])

if empatica_serial == 'A0069F':
    empatica_id = '7003BC' #E4 v1
elif empatica_serial == 'A00841':
    empatica_id = 'C22CBC' #E4 v1
elif empatica_serial == 'A00641':
    empatica_id = '84BBA7' #E4 v1
elif empatica_serial == 'A02766':
    empatica_id = '5EECCC' #E4 WA
elif empatica_serial == 'A02983':
    empatica_id = 'F1EBCC' #E4 WA
elif empatica_serial == 'A02D56':
    empatica_id = 'E5DCCC' #E4 WA
elif empatica_serial == 'A03740':
    empatica_id = '10048A' #E4 WA
elif empatica_serial == 'A0377A':
    empatica_id = '6E44C0' #E4 WA
elif empatica_serial == 'A0326E':
    empatica_id = '50DDCC' #E4 WA
elif empatica_serial == 'A02D0D':
    empatica_id = '8CDCCC' #E4 WA
elif empatica_serial == 'A02FA1':
    empatica_id = 'CF9CFD' #E4 WA
elif empatica_serial == 'A02648':
    empatica_id = 'DBEFCC' #E4 WA
elif empatica_serial == 'A03685':
    empatica_id = '6EC711' #E4 FR
elif empatica_serial == 'A03859':
    empatica_id = 'AFCB11' #E4 FR
elif empatica_serial == 'A03922':
    empatica_id = '13CE11' #E4 FR
elif empatica_serial == 'A0382A':
    empatica_id = '6CC711' #E4 FR

def connect_over_BTLE():
    
    global emp_sock
    emp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Connecting to server")
    emp_sock.connect((TCP_IP, TCP_PORT))
    print("Connected to server")

    print('Device available over BTLE')
    emp_sock.send('device_discover_list\r\n'.encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(repr(response))
    
    while empatica_id not in response.decode("utf-8"):
        emp_sock.send('device_discover_list\r\n'.encode())
        response = emp_sock.recv(BUFF_SIZE)
        print(repr(response))
        time.sleep(1)

    '''Device BTLE Connect'''
    emp_sock.send('device_connect_btle {} 180\r\n'.format(empatica_id).encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(repr(response))   
    while 'R device_connect_btle OK'.encode() not in response:
        emp_sock.send('device_connect_btle {} 180\r\n'.format(empatica_id).encode())
        response = emp_sock.recv(BUFF_SIZE)
        print(repr(response))
        time.sleep(1)

    outlet_error.push_sample([response.decode().strip('\n')])
    time.sleep(5)

if not gui:
    connect_over_BTLE()

def reconnect_over_BTLE():
    
    print('Device available over BTLE')
    emp_sock.send('device_discover_list\r\n'.encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(repr(response))
    
    while empatica_id not in response.decode("utf-8"):
        emp_sock.send('device_discover_list\r\n'.encode())
        response = emp_sock.recv(BUFF_SIZE)
        print(repr(response))
        time.sleep(1)

    '''Device BTLE Connect'''
    emp_sock.send('device_connect_btle {} 180\r\n'.format(empatica_id).encode())
    response = emp_sock.recv(BUFF_SIZE)        
    while 'R device_connect_btle OK'.encode() not in response:
        emp_sock.send('device_connect_btle {} 180\r\n'.format(empatica_id).encode())
        response = emp_sock.recv(BUFF_SIZE)
        print(repr(response))
        time.sleep(1)

    outlet_error.push_sample([response.decode().strip('\n')])
    time.sleep(5)

def connect():
    if gui:
        global emp_sock
        emp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        print("Connecting to server")
        emp_sock.connect((TCP_IP, TCP_PORT))
        print("Connected to server\n")

    print("Devices available:")
    emp_sock.send("device_list\r\n".encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(response.decode("utf-8"))

    '''Device Connect'''
    emp_sock.send('device_connect {}\r\n'.format(empatica_id).encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(repr(response))

    while 'R device_connect OK'.encode() not in response:
        emp_sock.send('device_connect {}\r\n'.format(empatica_id).encode())
        response = emp_sock.recv(BUFF_SIZE)
        print(repr(response))

    print("Pausing data receiving")
    emp_sock.send("pause ON\r\n".encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(repr(response))

    outlet_error.push_sample([response.decode().strip('\n')])
    # time.sleep(1)

connect()
time.sleep(1)

def reconnect_to_socket():

    global emp_sock
    emp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Connecting to server")
    emp_sock.connect((TCP_IP, TCP_PORT))
    print("Connected to server\n")

    print("Devices available:")
    emp_sock.send("device_list\r\n".encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(response.decode("utf-8"))

    '''Device Connect'''
    emp_sock.send('device_connect {}\r\n'.format(empatica_id).encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(repr(response))

    while 'R device_connect OK'.encode() not in response:
        emp_sock.send('device_connect {}\r\n'.format(empatica_id).encode())
        response = emp_sock.recv(BUFF_SIZE)
        print(repr(response))

    print("Pausing data receiving")
    emp_sock.send("pause ON\r\n".encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(repr(response))

    outlet_error.push_sample([response.decode().strip('\n')])
    # time.sleep(1)

def subscribe_to_data():
    '''Device Subscribe GSR'''
    emp_sock.send('device_subscribe gsr ON\r\n'.encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(repr(response))
    while 'R device_subscribe gsr OK'.encode() not in response:
        emp_sock.send('device_subscribe gsr ON\r\n'.encode())
        response = emp_sock.recv(BUFF_SIZE)
        print(repr(response))
    outlet_error.push_sample([response.decode().strip('\n')])

    if ppg_on:
        '''Device Subscribe BVP'''
        while 'R device_subscribe bvp OK'.encode() not in response:
            emp_sock.send('device_subscribe bvp ON\r\n'.encode())
            response = emp_sock.recv(BUFF_SIZE)
            print(repr(response))
        outlet_error.push_sample([response.decode().strip('\n')])

    '''Device Subscribe Battery'''
    while 'R device_subscribe bat OK'.encode() not in response:
        emp_sock.send('device_subscribe bat ON\r\n'.encode())
        response = emp_sock.recv(BUFF_SIZE)
        print(repr(response))
    outlet_error.push_sample([response.decode().strip('\n')])

    print("Resuming data receiving")
    emp_sock.send("pause OFF\r\n".encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(repr(response))

    outlet_error.push_sample(["Starting BS Recorder..."])

subscribe_to_data()

def disconnect():

    print("Disconnecting from device")
    emp_sock.send('device_disconnect\r\n'.encode())
    emp_sock.close()

def reconnect():
    if not gui:
        reconnect_over_BTLE()

    response = emp_sock.recv(BUFF_SIZE)            
    print(('Received', repr(response)))

    while 'connection re-established to device {}'.format(empatica_id) not in response.decode("utf-8"):
        response = emp_sock.recv(BUFF_SIZE)            
        print(('Received', repr(response)))

    print("Devices available:")
    emp_sock.send("device_list\r\n".encode())
    response = emp_sock.recv(BUFF_SIZE)
    print(response.decode("utf-8"))

    while empatica_id not in response.decode("utf-8"):
        print("Devices available:")
        emp_sock.send("device_list\r\n".encode())
        response = emp_sock.recv(BUFF_SIZE)
        print(response.decode("utf-8"))
        time.sleep(1)

    disconnect()

    print("Reconnecting...")
    if not gui:
        reconnect_to_socket()
    else:
        connect()

    subscribe_to_data()
    stream()

infoBVP = StreamInfo('{}_PPG'.format(empatica_serial),'PPG',1,FS_PPG,'float32','BVP-empatica_e4_{}'.format(empatica_id))
outlet_ppg = StreamOutlet(infoBVP)

infoGSR = StreamInfo('{}_GSR'.format(empatica_serial),'GSR',1,FS_GSR,'float32','GSR-empatica_e4_{}'.format(empatica_id))
outlet_gsr = StreamOutlet(infoGSR)        

info_bat = StreamInfo('{}_GSR_Battery'.format(empatica_serial), 'Marker', 1, 0, 'float32', 'BAT-empatica_e4_{}'.format(empatica_id))
outlet_bat = StreamOutlet(info_bat)

def stream():
    
    while True:

        cmd, cmd_ts = inlet_command.pull_sample(0.0)
        if cmd_ts:
            print(cmd[0])                
            if str(cmd[0]) == str("Close Device"):
                disconnect()
                time.sleep(2)
                sys.exit()
                
        try:
            data = emp_sock.recv(BUFF_SIZE).decode("utf-8")

            if 'connection lost to device' in data:
                print(data)
                outlet_error.push_sample([data])
                reconnect()
                break

            samples = data.split("\n")

            for i in range(len(samples)-1):
                stream_type = samples[i].split()[0]
                if stream_type == "E4_Bvp":
                    data = float(samples[i].split()[2].replace(',','.'))
                    outlet_ppg.push_sample([data])
                if stream_type == "E4_Gsr":
                    data = float(samples[i].split()[2].replace(',','.'))
                    outlet_gsr.push_sample([data])
                if stream_type == "E4_Battery":
                    data = float(samples[i].split()[2].replace(',','.'))
                    outlet_bat.push_sample([data])

        except socket.timeout:
            print("Socket timeout")
            reconnect()
            break

stream()