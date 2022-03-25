import sys
import os
from PyQt5 import QtWidgets,QtCore
import subprocess
from time import sleep
PATH = os.path.dirname(os.path.realpath(__file__))
#get the parent directory
PATH = PATH[0:-5]
sys.path.append(PATH)

import main

HOME=os.getenv("HOME")




def test_btn_create_snapshot(qtbot):
    MainWindow =main.Ui()
    mw= MainWindow
    mw.tabWidget.setCurrentIndex(1)
    
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
    
    
    
    
