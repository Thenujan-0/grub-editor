import subprocess
import logging
import traceback
from random import randint
import os
import sys


PATH = os.path.dirname(os.path.realpath(__file__))

ROOT_PATH=PATH[0:-6]
sys.path.append(ROOT_PATH)
print(ROOT_PATH)
import main

HOME=os.getenv("HOME")

def change_comboBox_current_index(mw):
    curr_ind = mw.comboBox_grub_default.currentIndex()
    
    for i in  range(len(mw.all_entries)):
        if i!= curr_ind:
            grub_default_ind = i
            break
    
    mw.comboBox_grub_default.setCurrentIndex(grub_default_ind)
    
    return grub_default_ind

def windows():
    """Returns windows names list and their id list in a tuple"""
    #shows all the visible windows
    exception_found=False
    while True:
        try:
            window_list=  subprocess.check_output(['wmctrl -l'],shell=True)
            window_list= window_list.decode()
            # printer(type(window_list))
            window_list=window_list.split('\n')
            # printer(window_list,'window_list')
            exception_found=False
        except Exception as e:
            exception_found=True
            print(str(e))
            print(traceback.format_exc())
            print('error in windows function call but it was handled like a boss😎')
            print('hope i aint struck in this loop 😅')
        finally:
            if not exception_found:
                break

    final_id_list =[]
    final_window_list =[]
    for window in window_list:
        window = window.split()
        # print(window)
        while True:
            if '' in window:
                window.remove('')
            else:
                break
    
        # print(window,'window')
        if len(window)>3:
            # printer(window)
            final_id_list.append(window[0])
            window.pop(0)
            window.pop(0)
            window.pop(0)

        # printer(window)
        tmp=''
        # print(window)
        for word in window:
            tmp = tmp+' '+word
        # printer(tmp)
        final_window_list.append(tmp[1:])
    # print(final_window_list)
    return final_window_list,final_id_list

def create_tmp_file(data):
    value =randint(0,20)
    tmp_file=f'{HOME}/.cache/grub-editor/temp{value}.txt'
    subprocess.run([f'touch {tmp_file}'],shell=True)
    
    with open(tmp_file,'w') as f:
        f.write(data)
    
    return tmp_file

def create_snapshot(data):
    num=randint(0,20)
    
    snapshot_name=f"{main.DATA_LOC}/snapshots/test_snapshot{num}"
    subprocess.run([f"touch {snapshot_name}"],shell=True)
    
    with open(snapshot_name,'w') as f:
        f.write(data)
    
    return f"test_snapshot{num}"
    