import unittest

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import main
import threading
from PyQt5 import QtWidgets,QtCore
import sys
from time import sleep
import pytest


def test_grub_timeout_add_substract(qtbot):
    
    
    Window = main.Ui()
    qtbot.addWidget(Window)
    
    time_out_val =Window.ledit_grub_timeout.text()
    print(time_out_val,'default grub_timeout_val')
    
    # click in the Greet button and make sure it updates the appropriate label
    qtbot.mouseClick(Window.btn_add, QtCore.Qt.LeftButton)
    assert Window.ledit_grub_timeout.text() == "21.0"
    qtbot.mouseClick(Window.btn_substract, QtCore.Qt.LeftButton)
    assert Window.ledit_grub_timeout.text()=='20.0'
    
    Window.tabWidget.setCurrentIndex(2) 
    Window.show()
    # qtbot.waitForWindowShown(Window)
    # with qtbot.waitExposed(Window):
        # pass
    # sleep(1)
    
    lv=Window.chroot.listWidget
    item =lv.item(0)
    rect = lv.visualItemRect(item)
    center = rect.center()
    print(center)
    print(item.text())
    assert lv.itemAt(center).text() == item.text()
    # assert lv.currentRow() == 0

    
    qtbot.mouseClick(Window.chroot.listWidget.viewport(),QtCore.Qt.LeftButton,pos=center)
    # Window.chroot.listWidget.item(2).click()
    assert type( Window.tabWidget.currentWidget()).__name__ =='ChrootAfterUi'
    currentWidget=Window.tabWidget.currentWidget()
    qtbot.mouseClick(currentWidget.btn_reinstall_grub_package,QtCore.Qt.LeftButton)
    with qtbot.waitExposed(Window):
        sleep(10)
    qtbot.stopForInteraction()
    

# app =QtWidgets.QApplication([])
# qtbot=QtBot()
# test_hello(qtbot)