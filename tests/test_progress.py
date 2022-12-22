import pytest
import os
import sys
from time import sleep
from PyQt5 import QtWidgets,QtCore
from tools import *

from widgets.progress import ProgressUi

def test_btn_show_details(qtbot):
    #mw is mainWindow
    mw=ProgressUi()
    qtbot.addWidget(mw)
    
    #click btn show details and check if scroll area is shown
    qtbot.mouseClick(mw.btn_show_details, QtCore.Qt.LeftButton)
    assert scrollArea_visible(mw,mw.verticalLayout)

    #check if btn show details is now named to hide details
    assert mw.verticalLayout.itemAt(2).widget().text()=='Hide details'
    
    #click hide details and check if it works
    qtbot.mouseClick(mw.btn_show_details,QtCore.Qt.LeftButton)
    assert mw.verticalLayout.itemAt(2).widget().text()=='Show details'
    assert  None == mw.verticalLayout.itemAt(3)
    
    
    
    # add another button to the window and then check if QScrollArea is created in right
    # place when btn_show_details is pressed
    btn_close =QtWidgets.QPushButton()
    btn_close.setText("Close")
    def btn_close_callback():
        print("this button isnt supposed to work")
        
    btn_close.clicked.connect(btn_close_callback)
    mw.verticalLayout.addWidget(btn_close)
    
    
    vcount =mw.verticalLayout.count()    
    #check if last widget is the close button
    assert   mw.verticalLayout.itemAt(vcount-1).widget().text() == 'Close'
    
    
    #now lets press the button
    qtbot.mouseClick(mw.btn_show_details,QtCore.Qt.LeftButton)
    
    #check if QScrollArea has been created in 3rd index
    assert scrollArea_visible(mw,mw.verticalLayout)
    
    line1="just pretend this is the first line of something important"
    
    mw.update_lbl_details(line1)
    
    assert mw.lbl_details_text ==line1
    
    assert mw.lbl_details.text()==line1

    line2="\npretent that this is the second line of some big text"
    mw.update_lbl_details(line2)
    
    assert mw.lbl_details_text ==line1+line2
    assert mw.lbl_details.text()==line1+line2
    
    #click hide details button and check if lbl_details_text percists
    qtbot.mouseClick(mw.btn_show_details,QtCore.Qt.LeftButton)
    
    assert mw.lbl_details_text ==line1+line2
    
    #now click show details and check if lbl_details has the text that it is supposed to have
    qtbot.mouseClick(mw.btn_show_details,QtCore.Qt.LeftButton)
    assert mw.lbl_details.text()==line1+line2
    

    
    