import sys
import os
from PyQt5 import QtWidgets,QtCore
import subprocess

PATH = os.path.dirname(os.path.realpath(__file__))
#get the parent directory
PATH = PATH[0:-5]
sys.path.append(PATH)

import main

HOME=os.getenv("HOME")

#delete the preferences file
subprocess.run([f"rm {HOME}/.grub-editor/preferences/main.json"],shell=True)


def test_btn_create_snapshot(qtbot):
    #todo
    pass

#test the view snapshot button
def test_btn_view(qtbot):
    
    #mw stand for mainWindow
    mw=main.Ui()
    main.MainWindow=mw;
    
    #first find the view btn of the first snapshots
    #before that we need to create a snapshot if no snapshots exist
    if mw.VLayout_snapshot.itemAt(0) is  None:
        qtbot.mouseClick(mw.btn_create_snapshot, QtCore.Qt.LeftButton)
    
    btn_view = mw.VLayout_snapshot.itemAt(0).layout().itemAt(2).widget()
    
    #check if it is view button
    assert btn_view.text()=='view'
    
    qtbot.mouseClick(btn_view, QtCore.Qt.LeftButton)
    
    
    
    #check if btn_view_window is visible
    assert mw.view_btn_win.isVisible()
    
