import os
import sys
import re
import subprocess
from time import sleep
from pathlib import Path
from PyQt5 import QtWidgets,QtCore,QtTest
from tools import change_comboBox_current_index,delete_pref


PATH = os.path.dirname(os.path.realpath(__file__))
#get the parent directory
PATH = Path(PATH).parent
sys.path.append(PATH)

import main

HOME=os.getenv("HOME")

def change_krnl_minor_vrsn(val)->str:
    #match the 14-1- like part of 5.16.14-1-
    pattern=r'\d+-\d+-'
    
    krnl_minor_vrsn=re.search(pattern,val).group(0)
    print(val)
    print(krnl_minor_vrsn)
    
    
    ind =krnl_minor_vrsn.find("-")
    krnl_minor_vrsn_strp=krnl_minor_vrsn[:ind]
    # new_ind = krnl_minor_vrsn[ind+1:].find("-") +ind
    # krnl_minor_vrsn = krnl_minor_vrsn[]
    
    print(krnl_minor_vrsn_strp)
    new_krnl_minor_vrsn_strp = str(int(krnl_minor_vrsn_strp)+1)
    new_krnl_minor_vrsn= krnl_minor_vrsn.replace(krnl_minor_vrsn_strp,new_krnl_minor_vrsn_strp)
    print(new_krnl_minor_vrsn)
    new_val = val.replace(krnl_minor_vrsn,new_krnl_minor_vrsn)
    print(new_val)
    return new_val

def test_fix_kernel_version_conf(qtbot):
    mw=main.Ui()
    main.MainWindow=mw
    if len(mw.invalid_entries)==0:
        for val in mw.all_entries:
            if " >" not in val:
                continue
            new_val=change_krnl_minor_vrsn(val)
            
            
            break
        print("changing the current entry to invalid")
        mw.close()
        main.initialize_temp_file()
        main.set_value("GRUB_DEFAULT=",new_val)
        subprocess.run([f"pkexec cp {HOME}/.cache/grub-editor/temp.txt /etc/default/grub"]
                       ,shell=True)
        mw = main.Ui()
        main.MainWindow=mw
        
    assert mw.dialog_invalid_default_entry.isVisible()
    
    #First press the cancel button check if window closes and 
    # no changes were made to the snapshot/file
    print(main.file_loc)
    old_sum = subprocess.check_output([f"sha256sum {main.file_loc}"],shell=True).decode()
    
    qtbot.mouseClick(mw.dialog_invalid_default_entry.btn_cancel,QtCore.Qt.LeftButton)
    
    new_sum =subprocess.check_output([f"sha256sum {main.file_loc}"],shell=True).decode()
    assert old_sum ==new_sum
    
    assert not mw.dialog_invalid_default_entry.isVisible()
    
    
    #Now lets press the fix button and check if it actually fixes the entry
    
    #first we need to call setUiElements to reshow that dialog
    mw.setUiElements(show_issues=True)
    
    assert mw.dialog_invalid_default_entry.isVisible()
    
    assert mw.comboBox_grub_default.currentIndex() == len(mw.all_entries)-1
    
    qtbot.mouseClick(mw.dialog_invalid_default_entry.btn_ok, QtCore.Qt.LeftButton)
    
    assert not mw.dialog_invalid_default_entry.isVisible()
    issues=[]
    with qtbot.waitSignal(mw.saveConfs_worker.signals.finished,timeout=30*1000):
        pass
    new_default_val = main.get_value("GRUB_DEFAULT=",issues)
    
    assert not issues
    assert new_default_val in mw.all_entries 
    assert new_default_val not in mw.invalid_entries
    
    
    
    
    
    
def test_fix_kernel_version_snapshot(qtbot):
    mw=main.Ui()
    main.MainWindow=mw
    
    if len(mw.invalid_entries)!=0:
        mw.dialog_invalid_default_entry.close()
        
    ind=2
    mw.comboBox_configurations.setCurrentIndex(2)
    #a snapshot would be selected now
    
    
        
    for val in mw.all_entries:
        if " >" not in val:
            continue
        
        new_val=change_krnl_minor_vrsn(val)
        break
    print("changing the current entry to invalid")
    mw.close()
    main.initialize_temp_file()
    main.set_value("GRUB_DEFAULT=",new_val)
    print(main.file_loc)
    subprocess.run([f"cp {HOME}/.cache/grub-editor/temp.txt {main.file_loc}"],shell=True)
    mw = main.Ui()
    main.MainWindow=mw
    mw.comboBox_configurations.setCurrentIndex(ind)
        
    assert mw.dialog_invalid_default_entry.isVisible()
    
    #First press the cancel button check if window closes and no changes were made to the snapshot/file
    print(main.file_loc,ind)
    
    old_sum = subprocess.check_output([f"sha256sum {main.file_loc}"],shell=True).decode()
    
    qtbot.mouseClick(mw.dialog_invalid_default_entry.btn_cancel,QtCore.Qt.LeftButton)
    
    new_sum =subprocess.check_output([f"sha256sum {main.file_loc}"],shell=True).decode()
    assert old_sum ==new_sum
    
    assert not mw.dialog_invalid_default_entry.isVisible()
    
    
    #Now lets press the fix button and check if it actually fixes the entry
    
    #first we need to call setUiElements to reshow that dialog
    mw.setUiElements(show_issues=True)
    
    assert mw.dialog_invalid_default_entry.isVisible()
    
    assert mw.comboBox_grub_default.currentIndex() == len(mw.all_entries)-1
    
    qtbot.mouseClick(mw.dialog_invalid_default_entry.btn_ok, QtCore.Qt.LeftButton)
    
    assert not mw.dialog_invalid_default_entry.isVisible()
    issues=[]
    
    new_default_val = main.get_value("GRUB_DEFAULT=",issues)
    
    assert not issues
    assert new_default_val in mw.all_entries 
    assert new_default_val not in mw.invalid_entries
    
    
def test_do_this_everytime(qtbot):
    
    
    
    mw = main.Ui()
    main.MainWindow=mw
        
    ind=2
    # -1 because lines has the list of snapshots but the configurations has /etc/default/grub
    target_snapshot=mw.lines[ind-1]
    target_snap_path=f'{main.DATA_LOC}/snapshots/{target_snapshot}'
    for val in mw.all_entries:
        if " >" not in val:
            continue
        
        new_val=change_krnl_minor_vrsn(val)
        break
    print("changing the current entry to invalid",new_val,target_snap_path)
    mw.close()
    main.set_value("GRUB_DEFAULT=",new_val,target_snap_path)
    mw = main.Ui()
    main.MainWindow=mw
    delete_pref()
    if len(mw.invalid_entries)!=0:
        mw.dialog_invalid_default_entry.close()
        
    pref=main.get_preference("invalid_kernel_version")
    assert pref is None
    mw.comboBox_configurations.setCurrentIndex(ind)
        
    assert mw.dialog_invalid_default_entry.isVisible()
    
    dialog =mw.dialog_invalid_default_entry
    QtTest.QTest.qWait(1000)
    print('done 1')
    pref=main.get_preference("invalid_kernel_version")
    assert pref is None
    
    if not dialog.checkBox.isChecked():
        mw.dialog_invalid_default_entry.checkBox.click()
    
    pref=main.get_preference("invalid_kernel_version")
    assert pref is None
        
    qtbot.mouseClick(dialog.btn_cancel, QtCore.Qt.LeftButton)
    
    # QtTest.QTest.qWait(10000)
    pref=main.get_preference("invalid_kernel_version")
    assert pref == "cancel"
    
    assert not dialog.isVisible()
    
    #to reshow the dialog
    mw.setUiElements()
    
    #close the dialog if it popped up for /etc/default/grub entry
    if len(mw.invalid_entries)>0:
        mw.dialog_invalid_default_entry.close()
    
    mw.comboBox_configurations.setCurrentIndex(ind)
    
    dialog=mw.dialog_invalid_default_entry
    assert not dialog.isVisible()
    
    
    