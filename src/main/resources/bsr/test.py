from unittest import main


from pylsl import StreamInfo, StreamOutlet, StreamInlet, resolve_byprop, local_clock
from utils.settings_class import BSRConfig,EEGConfig,GSRConfig,PPGConfig,AcqConfig

bsr_cfg = BSRConfig("start_config.xml")
use_eeg = bsr_cfg.use_eeg

eeg_cfg = EEGConfig(bsr_cfg.eeg_device)

info_command2EEGapp = StreamInfo('CommandFromGui_{}'.format(eeg_cfg.serial), 'Markers', 1, 0, 'string', 'myuidw43536')
print('CommandFromGui_{}'.format(eeg_cfg.serial))
outlet_command2EEGapp = StreamOutlet(info_command2EEGapp)

print('outlet')
outlet_command2EEGapp.push_sample(["Start Acquisition"])

# outlet_command2EEGapp.push_sample(["Start Acquisition"])