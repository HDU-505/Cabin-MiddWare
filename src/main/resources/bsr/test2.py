import sys
import threading
import psutil
import websocket
from pylsl import StreamInfo, StreamOutlet

from utils.settings_class import BSRConfig, EEGConfig, GSRConfig, PPGConfig

# 获取MAC地址
mac = None
for interface in psutil.net_if_addrs():
    if psutil.net_if_addrs()[interface][0].address:
        mac = psutil.net_if_addrs()[interface][0].address
        break

if mac is None:
    raise RuntimeError("MAC地址获取失败")

# Connection Settings
bsr_cfg = BSRConfig("start_config.xml")
use_eeg = bsr_cfg.use_eeg
use_gsr = bsr_cfg.use_gsr
use_ppg = bsr_cfg.use_ppg

eeg_cfg = EEGConfig(bsr_cfg.eeg_device)
gsr_cfg = GSRConfig(bsr_cfg.gsr_device)
ppg_cfg = PPGConfig(bsr_cfg.ppg_device)

if use_eeg:
    # Outlet that Sends commands to the EEG Amp App Controller
    print('CommandFromGui_{}'.format(eeg_cfg.serial) + "--------")
    try:
        info_command2EEGapp = StreamInfo('CommandFromGui_{}'.format(eeg_cfg.serial), 'Markers', 1, 0, 'string', 'myuidw43536')
        print('CommandFromGui_{}'.format(eeg_cfg.serial))
        outlet_command2EEGapp = StreamOutlet(info_command2EEGapp)
    except Exception as e:
        print("Error creating StreamOutlet:", e)
        sys.exit(1)

def listen_to_websocket():
    def on_message(ws, message):
        print('Received: ' + message)
        if message == 'calibration':
            try:
                outlet_command2EEGapp.push_sample(["Stop Acquisition"])
                outlet_command2EEGapp.push_sample(["Check Impedances"])
                print("Sent calibration commands successfully")
            except Exception as e:
                print("Error sending calibration commands:", e)
        if message == 'acquisition':
            try:
                outlet_command2EEGapp.push_sample(["Stop Check Impedances"])
                outlet_command2EEGapp.push_sample(["Start Acquisition"])
                print("Sent acquisition commands successfully")
            except Exception as e:
                print("Error sending acquisition commands:", e)
        sys.stdout.flush()  # 立即刷新缓冲区


    def on_open(ws):
        print("WebSocket client 'NeuroClient' connected")

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket client 'NeuroClient' disconnected with code:", close_status_code, "and message:", close_msg)

    def on_error(ws, error):
        print("WebSocket client 'NeuroClient' encountered an error:", error)

    ws = websocket.WebSocketApp(
        "ws://127.0.0.1:8888/websocket/w",
        on_message=on_message,
        on_open=on_open,
        on_close=on_close,
        on_error=on_error
    )
    ws.run_forever()

if __name__ == '__main__':
    ws_thread = threading.Thread(target=listen_to_websocket, name="NeuroClient_WebSocket_Listener")
    ws_thread.start()
