import threading
import time
import websocket
import psutil
from pylsl import StreamInfo, StreamOutlet
from utils.settings_class import BSRConfig, EEGConfig, GSRConfig, PPGConfig

# 获取本地网络接口的 MAC 地址
for interface in psutil.net_if_addrs():
    if psutil.net_if_addrs()[interface][0].address:
        mac = psutil.net_if_addrs()[interface][0].address
        break

# 连接设置
bsr_cfg = BSRConfig("start_config.xml")
use_eeg = bsr_cfg.use_eeg
use_gsr = bsr_cfg.use_gsr
use_ppg = bsr_cfg.use_ppg

eeg_cfg = EEGConfig(bsr_cfg.eeg_device)
gsr_cfg = GSRConfig(bsr_cfg.gsr_device)
ppg_cfg = PPGConfig(bsr_cfg.ppg_device)

if use_eeg:
    # 如果使用 EEG 设备
    print('CommandFromGui_{}'.format(eeg_cfg.serial)+"--------")
    info_command2EEGapp = StreamInfo('CommandFromGui_{}'.format(eeg_cfg.serial), 'Markers', 1, 0, 'string', 'myuidw43536')
    print('CommandFromGui_{}'.format(eeg_cfg.serial))
    outlet_command2EEGapp = StreamOutlet(info_command2EEGapp)

# WebSocket 服务器 URL
ws_url = "ws://127.0.0.1:8888/websocket/messageServer?username=touch_screen"

# 设置重试间隔时间（秒）
RETRY_INTERVAL = 5

def on_message(ws, message):
    print('Received: ' + message)
    if message == 'calibration':
        outlet_command2EEGapp.push_sample(["Stop Acquisition"])
        # sleep(500)
        outlet_command2EEGapp.push_sample(["Check Impedances"])
    if message == 'acquisition':
        outlet_command2EEGapp.push_sample(["Stop Check Impedances"])
        # sleep(500)
        outlet_command2EEGapp.push_sample(["Start Acquisition"])

def on_open(ws):
    print("WebSocket connection established.")

def on_close(ws):
    print("WebSocket connection closed.")

def connect_to_websocket():
    print("Connecting to WebSocket server...")
    while True:
        try:
            ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open, on_close=on_close)
            ws.run_forever()
        except Exception as e:
            print("WebSocket connection failed:", e)
            print("Retrying in", RETRY_INTERVAL, "seconds...")
            time.sleep(RETRY_INTERVAL)

if __name__ == '__main__':
    # 启动 WebSocket 连接线程
    ws_thread = threading.Thread(target=connect_to_websocket)
    ws_thread.start()
