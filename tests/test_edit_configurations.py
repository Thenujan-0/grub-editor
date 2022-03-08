import os;
import sys;


PATH=os.path.dirname(os.path.realpath(__file__))

#parent dir
PATH=PATH[0:-5]
sys.path.append(PATH)

import main
from PyQt5 import QtWidgets,QtCore


def test_grub_timeout_add_substract(qtbot):
    
    MainWindow = main.Ui()
    mw=MainWindow
    qtbot.addWidget(mw)
    
    time_out_val =mw.ledit_grub_timeout.text()
    print(time_out_val,'default grub_timeout_val')
    
    # click in the Greet button and make sure it updates the appropriate label
    qtbot.mouseClick(mw.btn_add, QtCore.Qt.LeftButton)
    assert mw.ledit_grub_timeout.text() == str(float(time_out_val)+1)
    qtbot.mouseClick(mw.btn_substract, QtCore.Qt.LeftButton)
    assert mw.ledit_grub_timeout.text()==str(float(time_out_val))
    
    #set the value of ledit_grub_timeout to 1 and then check if it goes below zero
    mw.ledit_grub_timeout.setText("1.0")
    qtbot.mouseClick(mw.btn_substract, QtCore.Qt.LeftButton)
    assert mw.ledit_grub_timeout.text() == "0.0"
    qtbot.mouseClick(mw.btn_substract, QtCore.Qt.LeftButton)
    assert mw.ledit_grub_timeout.text() == "0.0"
    
    
    
    
    
    
    
