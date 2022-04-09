import os;
import sys;
from time import sleep
from PyQt5 import QtWidgets,QtCore
import subprocess


HOME =os.getenv('HOME')
PATH=os.path.dirname(os.path.realpath(__file__))

#parent dir
PATH=PATH[0:-5]
sys.path.append(PATH)

import main


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
    
    
    
    
def test_look_for_other_os(qtbot):
    MainWindow = main.Ui()
    mw=MainWindow
    qtbot.addWidget(mw)
    
    cb=mw.checkBox_look_for_other_os
    cb.setChecked(False)
    
    assert cb.isChecked() ==False  

    main.set_value("GRUB_DISABLE_OS_PROBER=","false")
    
    save_btn=mw.btn_set
    qtbot.mouseClick(mw.btn_set, QtCore.Qt.LeftButton)
    sleep(1)
    assert mw.lbl_status.text() =="Waiting for authentication"
    sleep(3)
    
    #might fail if password wasnt entered in 3 seconds
    assert mw.lbl_status.text() =="Saving configurations"
    while True:
        if mw.lbl_status.text()=="Saving configurations":
            sleep(1)
        else:
            break
        
        
 
    issues=[]
    assert main.get_value("GRUB_DISABLE_OS_PROBER=",issues)=="true"
    assert issues ==[]
    
    assert mw.lbl_status.text() =="Saved successfully"
    
    
    
    #repeat the same test but now the opposite case
    
    cb=mw.checkBox_look_for_other_os
    cb.setChecked(True)
    
    assert cb.isChecked() ==True  

    main.set_value("GRUB_DISABLE_OS_PROBER=","true")
    
    save_btn=mw.btn_set
    #todo
    qtbot.mouseClick(mw.btn_set, QtCore.Qt.LeftButton)
    sleep(1)
    assert mw.lbl_status.text() =="Waiting for authentication"
    sleep(3)
    assert mw.lbl_status.text() =="Saving configurations"
    while True:
        if mw.lbl_status.text()=="Saving configurations":
            sleep(1)
        else:
            break
        
        

    issues=[]
    assert main.get_value("GRUB_DISABLE_OS_PROBER=",issues)=="false"
    assert issues ==[]
            
    
    assert mw.lbl_status.text() =="Saved successfully"
    
def test_comboBox_configurations(qtbot):
    MainWindow = main.Ui()
    mw=MainWindow
    qtbot.addWidget(mw)
    for i in range(len(mw.all_entries)):
        if i != mw.comboBox_grub_default.currentIndex():
            temp_entry = mw.all_entries[i]
            break
    
    
    snapshot_test="""GRUB_DEFAULT="""
    subprocess.run([f' echo "{snapshot_test}" > {HOME}/.grub-editor/snapshots/test_snapshot'],shell=True)
    main.set_value("GRUB_DEFAULT=",temp_entry,target_file=f"{HOME}/.grub-editor/snapshots/test_snapshot")
    mw.comboBox_configurations.setCurrentIndex(mw.configurations.index("test_snapshot"))

    
    #check if the correct value for grub default was shown
    assert mw.all_entries[mw.comboBox_grub_default.currentIndex()] ==temp_entry
    
    
    
