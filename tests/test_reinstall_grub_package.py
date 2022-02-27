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
    
    
    widget = main.Ui()
    qtbot.addWidget(widget)
    # click in the Greet button and make sure it updates the appropriate label
    qtbot.mouseClick(widget.btn_add, QtCore.Qt.LeftButton)
    assert widget.ledit_grub_timeout.text() == "21.0"
    qtbot.mouseClick(widget.btn_substract, QtCore.Qt.LeftButton)
    assert widget.ledit_grub_timeout.text()=='20.0'
    
    widget.tabWidget.setCurrentIndex(2) 
    widget.show()
    # qtbot.waitForWindowShown(widget)
    with qtbot.waitExposed(widget):
        pass
    sleep(1)
    
    lv=widget.chroot.listWidget
    item =lv.item(0)
    rect = lv.visualItemRect(item)
    center = rect.center()
    print(center)
    print(item.text())
    assert lv.itemAt(center).text() == item.text()
    assert lv.currentRow() == 0

    
    qtbot.mouseClick(widget.chroot.listWidget.viewport(),QtCore.Qt.LeftButton,pos=center)
    # widget.chroot.listWidget.item(2).click()
    assert type( widget.tabWidget.currentWidget()).__name__ =='ChrootAfterUi'
    currentWidget=widget.tabWidget.currentWidget()
    qtbot.mouseClick(currentWidget.btn_reinstall_grub_package,QtCore.Qt.LeftButton)
    with qtbot.waitExposed(widget):
        sleep(10)
    qtbot.stopForInteraction()
    

# app =QtWidgets.QApplication([])
# qtbot=QtBot()
# test_hello(qtbot)