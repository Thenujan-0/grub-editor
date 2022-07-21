""" Tools for testing """

import subprocess
import traceback
from random import randint
import os
import sys

from pathlib import Path



PATH=os.path.dirname(os.path.realpath(__file__))
PARENT_PATH=str(Path(PATH).parent)



sys.path.append(PARENT_PATH)
import main

HOME=os.getenv("HOME")

def change_comboBox_current_index(mw):
    """ Changes the current index of the combobox default entries
        for numbers from 0 - max it will put the minimum that is not current value
    """
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
    """ Creates a file with the data provided as argument and returns the name of file """
    value =randint(0,20)
    tmp_file=f'{HOME}/.cache/grub-editor/temp{value}.txt'
    subprocess.run([f'touch {tmp_file}'],shell=True)
    
    with open(tmp_file,'w') as f:
        f.write(data)
    
    return tmp_file

def create_test_file(data):
    """ Creates a file with the data provided as argument and returns the name of file """
    value =randint(0,20)
    test_file=f'{HOME}/.cache/grub-editor/test{value}.txt'
    subprocess.run([f'touch {test_file}'],shell=True)
    
    with open(test_file,'w') as f:
        f.write(data)
    
    return test_file

def create_snapshot(data):
    """ Create a snapshot with the data provided as argument 
        and returns the name of the snapshot
        Eg name: test_snapshot0
        Snapshot path is f"{main.DATA_LOC}/snapshots/"
    
    """
    num=randint(0,20)
    
    snapshot_name=f"{main.DATA_LOC}/snapshots/test_snapshot{num}"
    subprocess.run([f"touch {snapshot_name}"],shell=True)
    
    with open(snapshot_name,'w') as f:
        f.write(data)
    
    return f"test_snapshot{num}"

def scrollArea_visible(mw,targetLayout=None)->bool:
    """ Checks if the scroll area which shows more details is visible
        Warning:dependant on the current layout of window. May fail if a new widget was inserted
    """
    if targetLayout is None:
        targetLayout=mw.verticalLayout_2
        
    print(targetLayout.count())
    for i in range(targetLayout.count()):
        print(i,targetLayout.itemAt(i).widget())
        if 'QScrollArea' in str(targetLayout.itemAt(i).widget()):
            return True
    return False
    
    
def password_not_entered(mw):
    return mw.lbl_status.text() =="Waiting for authentication"

def delete_pref():
    """ Deletes the user preference file """
    subprocess.run([f"rm {main.CONFIG_LOC}/main.json"],shell=True)