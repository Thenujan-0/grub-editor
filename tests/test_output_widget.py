import os
import sys
from time import sleep
from PyQt5 import QtWidgets,QtCore,QtTest
from tools import *
from grubEditor import main

def test_no_show_details(qtbot):
    """ Test the usage of show_details btn when update-grub is performed """
    
    mw=main.Ui()
    main.MainWindow=mw
    main.DEBUG=True
    
    qtbot.mouseClick(mw.btn_add,QtCore.Qt.LeftButton)
    assert not scrollArea_visible(mw)
    
    #click btn set and check scroll area part is invisible
    qtbot.mouseClick(mw.btn_set,QtCore.Qt.LeftButton)
    assert not scrollArea_visible(mw)
    
    while password_not_entered(mw):
        sleep(1)
    print("count",mw.verticalLayout.count())
    
    
    #click show details and check if scroll area is visible
    qtbot.mouseClick(mw.btn_show_details,QtCore.Qt.LeftButton)
    assert scrollArea_visible(mw)
    
    #Now click hide details button and check if scroll area is invisible
    qtbot.mouseClick(mw.btn_show_details,QtCore.Qt.LeftButton)
    assert not scrollArea_visible(mw)
    
    QtTest.QTest.qWait(1000)
    
    #Now repeat the same process again
    #click show details and check if scroll area is visible
    qtbot.mouseClick(mw.btn_show_details,QtCore.Qt.LeftButton)
    assert scrollArea_visible(mw)
    
    #Now click hide details button and check if scroll area is invisible
    qtbot.mouseClick(mw.btn_show_details,QtCore.Qt.LeftButton)
    assert not scrollArea_visible(mw)
    