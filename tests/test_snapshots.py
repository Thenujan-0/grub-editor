import sys
import os
from PyQt5 import QtWidgets,QtCore
import subprocess
from time import sleep
from datetime import datetime as dt
import re
from tools import change_comboBox_current_index , windows
PATH = os.path.dirname(os.path.realpath(__file__))
#get the parent directory
PATH = PATH[0:-5]
sys.path.append(PATH)

import main

HOME=os.getenv("HOME")

#checks if modified is shown but the main purpose of this function is to use it in other tests
def test_change_config_modified(qtbot):
    #mw stand for mainWindow
    mw=main.Ui()
    main.MainWindow=mw;
    curr_ind = mw.comboBox_grub_default.currentIndex()
    for i in  range(len(mw.all_entries)):
        if i!= curr_ind:
            pass
            grub_default_ind = i
            break
    # todo here
    mw.comboBox_grub_default.setCurrentIndex(grub_default_ind)




def _test_ignore_changes(qtbot,mw,grub_default_ind):
    ''' Assumes that the grub default is in modified state '''

    
    #read data from /etc/default/grub
    with open('/etc/default/grub') as f:
        conf_data = f.read()
    
    assert mw.comboBox_grub_default in mw.original_modifiers
    
    
    qtbot.mouseClick(mw.create_snapshot_dialog.btn_ignore_changes, QtCore.Qt.LeftButton)
    
    assert not mw.create_snapshot_dialog.isVisible()
    date_time =str(dt.now()).replace(' ','_')[:-7]
    
    snapshots =[]
    for i in range(len(mw.configurations)):
        snapshots.append(mw.comboBox_configurations.itemText(i))
    
    
    #check if a snapshot was created
    for i in range(len(mw.configurations)):
        item_text=mw.comboBox_configurations.itemText(i)
        try:
            snapshots.remove(item_text)
        except:
            if '(modified)' not in item_text:
                assert item_text==date_time
                break
    
    #check if new snapshot actually ignored the changes
    with open(f'{HOME}/.grub-editor/snapshots/{date_time}') as f:
        new_data =f.read()
    
    assert new_data ==conf_data
    
    assert grub_default_ind == mw.comboBox_grub_default.currentIndex()
    
    #check if it is showing a modified version of /etc/default/grub  
    
    assert '(modified)' in mw.configurations[mw.comboBox_configurations.currentIndex()]


def _test_add_changes_snapshot(qtbot,mw):
    #now lets do the same test but with btn_add_changes_to_snapshot


    
    date_time =str(dt.now()).replace(' ','_')[:-7]
    
    snapshots =[]
    for i in range(len(mw.configurations)):
        snapshots.append(mw.comboBox_configurations.itemText(i))
    
    
    #check if a snapshot was created
    for i in range(len(mw.configurations)):
        try:
            snapshots.remove(mw.comboBox_configurations.itemText(i))
        except:
            if '(modified)' not in mw.comboBox_configurations.itemText(i):
                assert mw.comboBox_configurations.itemText(i)==date_time
                break
            
    #check if it is showing a modified version of /etc/default/grub  
    assert '(modified)' in mw.configurations[mw.comboBox_configurations.currentIndex()]
    
    new_snapshot=f'{HOME}/.grub-editor/snapshots/{date_time}'
    with open(new_snapshot) as f:
        new_data = f.read()
        
    diff_out = subprocess.run([f"diff {new_snapshot} /etc/default/grub"],shell=True,capture_output=True).stdout.decode()
    
    lines = diff_out.splitlines()
    print(lines)
    #first line would be something like 1c1 or 2c2
    assert lines[0][0]==lines[0][2]
    assert lines[0][1]=='c'
    
    assert 'GRUB_DEFAULT=' in lines[1]
    assert 'GRUB_DEFAULT=' in lines[3]

def test_btn_create_snapshot(qtbot):
    #mw stand for mainWindow
    mw=main.Ui()
    main.MainWindow=mw;
    mw.tabWidget.setCurrentIndex(1)
    qtbot.addWidget(mw)
    
    #check if another configuration gets added when btn_create_snapshot is pressed
    snapshots_count =len(mw.configurations)-1
    qtbot.mouseClick(mw.btn_create_snapshot,QtCore.Qt.LeftButton)
    new_snapshots_count=len(mw.configurations)-1
    assert new_snapshots_count -1== snapshots_count
    
    

    
    #get to the edit_configurations tab  and then change something to check if a new windows open ups to ask which
    #   configuration i want to save to snapshot (from the file or edited one)
    mw.tabWidget.setCurrentIndex(0)
    
    grub_default_ind=change_comboBox_current_index(mw)
    assert '(modified)' in mw.configurations[mw.comboBox_configurations.currentIndex()]
    
    mw.tabWidget.setCurrentIndex(1)
    
    #remove default preference 
    main.set_preference("create_snapshot","None")
    
    
    qtbot.mouseClick(mw.btn_create_snapshot,QtCore.Qt.LeftButton)
        
    assert mw.create_snapshot_dialog.isVisible()
    
    qtbot.mouseClick(mw.btn_create_snapshot,QtCore.Qt.LeftButton)
        
    assert mw.create_snapshot_dialog.isVisible()
    
    _test_ignore_changes(qtbot,mw,grub_default_ind)
    
    
    
    qtbot.mouseClick(mw.create_snapshot_dialog.btn_add_changes_to_snapshot, QtCore.Qt.LeftButton)
    assert not  mw.create_snapshot_dialog.isVisible()
    
    _test_add_changes_snapshot(qtbot,mw)

def test_btn_delete_snapshot(qtbot):
    #mw stand for mainWindow
    mw=main.Ui()
    main.MainWindow=mw;
    mw.tabWidget.setCurrentIndex(1)
    
    snapshots = []
    for i in range(len(mw.configurations)):
        snapshots.append(mw.comboBox_configurations.itemText(i))
    
    date_time =str(dt.now()).replace(' ','_')[:-7]
    
    qtbot.mouseClick(mw.btn_create_snapshot, QtCore.Qt.LeftButton)
    
    snapshot_is_in_list_var= False
    #check if a snapshot was created
    for i in range(len(mw.configurations)):
        try:
            snapshots.remove(mw.comboBox_configurations.itemText(i))
        except ValueError:
            if '(modified)' not in mw.comboBox_configurations.itemText(i):
                if mw.comboBox_configurations.itemText(i)==date_time:
                    snapshot_is_in_list_var =True
                    break
    assert snapshot_is_in_list_var==True
    
    for i in range(mw.VLayout_snapshot.count()):
        text =mw.VLayout_snapshot.itemAt(i).itemAt(0).widget().text()
        if text == date_time:
            new_snapshot_ind = i
            break
    assert main.CONF_LOC== mw.configurations[mw.comboBox_configurations.currentIndex()]
    
    #now that we have found the index of the snapshot we have just created 
    #Lets find the delete btn of the snapshot
    print(i)
    target_snapshot_row=mw.VLayout_snapshot.itemAt(new_snapshot_ind)
    btn_delete = target_snapshot_row.itemAt(3).widget()
    
    assert target_snapshot_row.itemAt(0).widget().text()==date_time
    
    mw.tabWidget.setCurrentIndex(0)
    
    #change something the edit_configurations UI and check if the value persists after deleti
    mw.btn_substract.click()
    assert '(modified)' in mw.configurations[mw.comboBox_configurations.currentIndex()]
    
    #get current value of grub timeout
    old_val = mw.ledit_grub_timeout.text()
    
    mw.tabWidget.setCurrentIndex(1)
    
    qtbot.mouseClick(btn_delete,QtCore.Qt.LeftButton)
    sleep(1)
    assert main.CONF_LOC+"(modified)"== mw.configurations[mw.comboBox_configurations.currentIndex()]
    
    assert mw.VLayout_snapshot.itemAt(new_snapshot_ind).itemAt(3).widget() != btn_delete

    assert '(modified)' in mw.configurations[mw.comboBox_configurations.currentIndex()]
    
    mw.tabWidget.setCurrentIndex(0)
    
    #get the new value of grub timeout
    assert mw.ledit_grub_timeout.text()  == old_val
    
    assert '(modified)' in mw.configurations[mw.comboBox_configurations.currentIndex()]
    
    
    

#test the view snapshot button
def test_btn_view(qtbot):
    
    #mw stand for mainWindow
    mw=main.Ui()
    main.MainWindow=mw;
    
    #first find the view btn of the first snapshots
    #before that we need to create a snapshot if no snapshots exist
    if mw.VLayout_snapshot.itemAt(0) is  None:
        qtbot.mouseClick(mw.btn_create_snapshot, QtCore.Qt.LeftButton)
    
    snapshot_name =mw.VLayout_snapshot.itemAt(0).layout().itemAt(0).widget().text()
    btn_view = mw.VLayout_snapshot.itemAt(0).layout().itemAt(2).widget()
    
    #check if it is view button
    assert btn_view.text()=='view'
    
    #delete the preferences file
    subprocess.run([f"rm {HOME}/.grub-editor/preferences/main.json"],shell=True)
    
    qtbot.mouseClick(btn_view, QtCore.Qt.LeftButton)
    
    
    #check if btn_view_window is visible
    assert mw.view_btn_win.isVisible()
    
    mw.view_btn_win.close()
    
    
    #now check if that view_btn_win opens when preference has a value 
    main.set_preference("view_default","default_text_editor")
    
    qtbot.mouseClick(btn_view,QtCore.Qt.LeftButton)
    assert not mw.view_btn_win.isVisible()
    assert mw.comboBox_configurations.currentText() =='/etc/default/grub'
    
    #! only works when kate is default text editor if not test has to be changed
    #might fail when kate takes too long to load
    sleep(5)
    windows= subprocess.check_output(["wmctrl -l "],shell=True).decode()
    assert f"{snapshot_name}  — Kate" in windows
    
    main.set_preference("view_default","on_the_application_itself")
    
    qtbot.mouseClick(btn_view,QtCore.Qt.LeftButton)
    assert not mw.view_btn_win.isVisible()
    assert mw.tabWidget.currentIndex() ==0
    
    assert mw.comboBox_configurations.currentText() ==f"{snapshot_name}"
    
    
    
    
def test_btn_set(qtbot):
    mw=main.Ui()
    main.MainWindow=mw
    #todo make a failing test as set button currently faulty
    mw.tabWidget.setCurrentIndex(1)
    
    
    if mw.VLayout_snapshot.count()==0:
        qtbot.mouseClick(mw.btn_create_snapshot,QtCore.Qt.LeftButton)
    
    row=mw.VLayout_snapshot.itemAt(0).layout()
    btn_set = row.itemAt(4).widget()
    snapshot_name=row.itemAt(0).widget().text()
    assert main.file_loc==main.CONF_LOC
    qtbot.mouseClick(btn_set,QtCore.Qt.LeftButton)
    
    assert mw.lbl_status.text() =="Waiting for authentication"
    sleep(1)
    win_list=windows()[0]
    auth_win_vis=False
    for i in range(len(win_list)):
        print(win_list[i])
        if "Authentication Required — PolicyKit1" in win_list[i]:
            auth_win_vis=True
            break
    
    assert auth_win_vis==True
    
    with qtbot.waitSignal(mw.set_snapshot_worker.signals.finished,timeout=30*1000):
        pass

    conf_sum = subprocess.check_output([f"sha256sum {main.CONF_LOC}"],shell=True).decode()
    snapshot_sum = subprocess.check_output([f"sha256sum {HOME}/.grub-editor/snapshots/{snapshot_name}"],shell=True).decode()
    assert conf_sum[:65]==snapshot_sum[:65]