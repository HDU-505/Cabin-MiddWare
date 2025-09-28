'''
Created on 14 nov 2017

@author: Antonello
'''

import os

def create_filename(id_sess_name,filename_2save,bsr_cfg):
    
    filename_2open_eeg = None
    filename_2open_gsr = None
    filename_2open_ppg = None
    filename_2open_mrk = None

    if bsr_cfg.eeg_device == 'liveAmp':
        eeg_dev_name = 'la'
    elif bsr_cfg.eeg_device == 'touch':
        eeg_dev_name = 'th'
    elif bsr_cfg.eeg_device == 'muse':
        eeg_dev_name = 'mu'
            
    save_path = os.path.join("Data",id_sess_name)

    if str(filename_2save) is '':
    
        files = os.listdir(save_path)
        
        enumerated_files = [f for f in files if 'R0' in f and '_mrk' in f]
        not_named_file = [f for f in enumerated_files if f.strip(id_sess_name).strip('_mrk.dat').__len__() == 4]
        if not_named_file.__len__() > 0:
            not_named_file.sort()
            last_run = int(not_named_file[-1][not_named_file[-1].find('_')-2:not_named_file[-1].find('_')])
            if last_run < 9:
                run = "0{}".format(last_run+1)
            else:
                run = str(last_run+1)
        else:
            run = "01"
        
        id_sess_run_name_mrk = "{}R0{}_mrk.dat".format(id_sess_name,run)
        if bsr_cfg.use_eeg:
            id_sess_run_name_eeg = "{}R0{}_{}_eeg.dat".format(id_sess_name,run,eeg_dev_name)
        if bsr_cfg.use_gsr:
            id_sess_run_name_gsr = "{}R0{}_{}_gsr.dat".format(id_sess_name,run,bsr_cfg.gsr_device[:2])
        if bsr_cfg.use_ppg:
            id_sess_run_name_ppg = "{}R0{}_{}_ppg.dat".format(id_sess_name,run,bsr_cfg.ppg_device[:2])
                        
    else:
        id_sess_run_name_mrk = "{}{}_mrk.dat".format(id_sess_name,filename_2save)
        if bsr_cfg.use_eeg:
            id_sess_run_name_eeg = "{}{}_{}_eeg.dat".format(id_sess_name,filename_2save,eeg_dev_name)
        if bsr_cfg.use_gsr:
            id_sess_run_name_gsr = "{}{}_{}_gsr.dat".format(id_sess_name,filename_2save,bsr_cfg.gsr_device[:2])
        if bsr_cfg.use_ppg:
            id_sess_run_name_ppg = "{}{}_{}_ppg.dat".format(id_sess_name,filename_2save,bsr_cfg.ppg_device[:2])

        if os.path.exists(os.path.join(save_path,id_sess_run_name_mrk)):
            files = os.listdir(save_path)
            last_existing_file = [f for f in files if "{}{}".format(id_sess_name,filename_2save) in f]
            enum_last_existing_files = [f for f in last_existing_file if "R0" in f[f.find('_')-4:f.find('_')-2]]

            if enum_last_existing_files.__len__() > 0:
                enum_last_existing_files.sort()
                last_run = enum_last_existing_files[-1][enum_last_existing_files[-1].find('_')-2:enum_last_existing_files[-1].find('_')]
                last_run = int(last_run)
                if last_run < 9:
                    run = "0{}".format(last_run+1)
                else:
                    run = str(last_run+1)
            else:
                run = "01"
            id_sess_run_name_mrk = "{}{}R0{}_mrk.dat".format(id_sess_name,filename_2save,run)
            if bsr_cfg.use_eeg:
                id_sess_run_name_eeg = "{}{}R0{}_{}_eeg.dat".format(id_sess_name,filename_2save,run,eeg_dev_name)
            if bsr_cfg.use_gsr:
                id_sess_run_name_gsr = "{}{}R0{}_{}_gsr.dat".format(id_sess_name,filename_2save,run,bsr_cfg.gsr_device[:2])
            if bsr_cfg.use_ppg:
                id_sess_run_name_ppg = "{}{}R0{}_{}_ppg.dat".format(id_sess_name,filename_2save,run,bsr_cfg.ppg_device[:2])

    if bsr_cfg.use_eeg:
        filename_2open_eeg = os.path.join(save_path,id_sess_run_name_eeg)
    if bsr_cfg.use_gsr:
        filename_2open_gsr = os.path.join(save_path,id_sess_run_name_gsr)
    if bsr_cfg.use_ppg:
        filename_2open_ppg = os.path.join(save_path,id_sess_run_name_ppg)

    filename_2open_mrk = os.path.join(save_path,id_sess_run_name_mrk)
    
    return filename_2open_eeg,filename_2open_gsr,filename_2open_ppg,filename_2open_mrk

def create_filename_online(id_sess_name,bsr_cfg):
    
    filename_2open_eeg = None
    filename_2open_gsr = None
    filename_2open_ppg = None
    filename_2open_mrk = None

    if bsr_cfg.eeg_device == 'liveAmp':
        eeg_dev_name = 'la'
    elif bsr_cfg.eeg_device == 'touch':
        eeg_dev_name = 'th'
    elif bsr_cfg.eeg_device == 'muse':
        eeg_dev_name = 'mu'

    sub_folder = os.path.join("Data",id_sess_name)
    raw_save_path = os.path.join(sub_folder,"Raw")
    
    if not os.path.exists(raw_save_path):
        os.mkdir(raw_save_path)
    
    files = os.listdir(raw_save_path)
    not_named_file = []
    
    not_named_file = [f for f in files if 'R0' in f and '_mrk' in f]
    if not_named_file.__len__() > 0:
        not_named_file.sort()
        last_run = int(not_named_file[-1][not_named_file[-1].find('_')-2:not_named_file[-1].find('_')])
        if last_run < 9:
            run = "0{}".format(last_run+1)
        else:
            run = str(last_run+1)
    else:
        run = "01"

    id_sess_run_name_mrk = "{}R0{}_mrk.dat".format(id_sess_name,str(run))
    filename_2open_mrk = os.path.join(raw_save_path,id_sess_run_name_mrk)
    
    if bsr_cfg.use_eeg:
        id_sess_run_name_eeg = "{}R0{}_{}_eeg.dat".format(id_sess_name,str(run),eeg_dev_name)
        filename_2open_eeg = os.path.join(raw_save_path,id_sess_run_name_eeg)
    if bsr_cfg.use_gsr:
        id_sess_run_name_gsr = "{}R0{}_{}_gsr.dat".format(id_sess_name,str(run),bsr_cfg.gsr_device[:2])
        filename_2open_gsr = os.path.join(raw_save_path,id_sess_run_name_gsr)
    if bsr_cfg.use_ppg:
        id_sess_run_name_ppg = "{}R0{}_{}_ppg.dat".format(id_sess_name,str(run),bsr_cfg.ppg_device[:2])
        filename_2open_ppg = os.path.join(raw_save_path,id_sess_run_name_ppg)

    return filename_2open_eeg,filename_2open_gsr,filename_2open_ppg,filename_2open_mrk

def compute_inlet_timeout(bsr_cfg):
    
    inlet_timeout = {}

    if bsr_cfg.use_eeg:
        if bsr_cfg.eeg_device == 'liveAmp':
            inlet_timeout['eeg']=0.1
        elif bsr_cfg.eeg_device == 'touch':
            inlet_timeout['eeg']=0.2
        elif bsr_cfg.eeg_device == 'muse':
            inlet_timeout['eeg']=0.1
        inlet_timeout['gsr']=0.0
        inlet_timeout['ppg']=0.0
    elif not bsr_cfg.use_eeg and bsr_cfg.use_ppg:
        inlet_timeout['ppg']=0.125
        inlet_timeout['gsr']=0.0
    elif not bsr_cfg.use_eeg and not bsr_cfg.use_ppg and bsr_cfg.use_gsr:
        if bsr_cfg.gsr_device == 'shimmer':
            inlet_timeout['gsr']=0.125
        elif bsr_cfg.gsr_device == 'empatica':
            inlet_timeout['gsr']=0.25

    return inlet_timeout
