import sys
import os
from PyQt5 import QtWidgets,QtCore
import subprocess
from time import sleep
from datetime import datetime as dt
import re

PATH = os.path.dirname(os.path.realpath(__file__))
#get the parent directory
PATH = PATH[0:-5]
sys.path.append(PATH)

import main

HOME=os.getenv("HOME")

#checks if modified is shown but the main purpose of this function is to use it in other tests
def test_change_all_config(qtbot):
    MainWindow =main.Ui()
    mw= MainWindow
    curr_ind = mw.comboBox_grub_de
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
    MainWindow =main.Ui()
    mw= MainWindow
    mw.tabWidget.setCurrentIndex(1)
    qtbot.addWidget(mw)
    
    #check if another configuration gets added when btn_create_snapshot is pressed
    snapshots_count =len(mw.configurations)-1
    qtbot.mouseClick(mw.btn_create_snapshot,QtCore.Qt.LeftButton)
    new_snapshots_count=len(mw.configurations)-1
    assert new_snapshots_count -1== snapshots_count
    
    

    
    #get to the edit_configurations tab  and then change something to check if a new windows open ups to ask which
    #   configuration i want to change
    mw.tabWidget.setCurrentIndex(0)
    curr_ind = mw.comboBox_grub_default.currentIndex()
    
    for i in  range(len(mw.all_entries)):
        if i!= curr_ind:
            pass
            grub_default_ind = i
            break
    
    mw.comboBox_grub_default.setCurrentIndex(grub_default_ind)
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
    MainWindow =main.Ui()
    mw= MainWindow
    mw.tabWidget.setCurrentIndex(1)
    
    snapshots = []
    for i in range(len(mw.configurations)):
        snapshots.append(mw.comboBox_configurations.itemText(i))
    
    date_time =str(dt.now()).replace(' ','_')[:-7]
    
    qtbot.mouseClick(mw.btn_create_snapshot, QtCore.Qt.LeftButton)
    
    #check if a snapshot was created
    for i in range(len(mw.configurations)):
        try:
            snapshots.remove(mw.comboBox_configurations.itemText(i))
        except:
            if '(modified)' not in mw.comboBox_configurations.itemText(i):
                if mw.comboBox_configurations.itemText(i)==date_time:
                    new_snapshot_ind=i
                    break
    
    #now that we have found the index of the snapshot we have just created 
    #Lets find the delete btn of the snapshot
    btn_delete = mw.VLayout_snapshot.itemAt(new_snapshot_ind).itemAt(2).widget()
    
    #todo 
    qtbot.mouseClick(btn_delete,QtCore.Qt.LeftButton)
    
    
    

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
    
    
    
    
