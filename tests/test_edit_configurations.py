import os;
import sys;
from time import sleep
from PyQt5 import QtWidgets,QtCore
import subprocess
from tools import change_comboBox_current_index ,create_tmp_file,create_snapshot

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
    
    cb =mw.checkBox_look_for_other_os
    
    
    if  not cb.isChecked():
        main.initialize_temp_file()
        main.set_value("GRUB_DISABLE_OS_PROBER=","false")
        mw.saveConfs()
    
    
    #h
        with qtbot.waitSignal(mw.saveConfs_worker.signals.finished,timeout=30*1000):
            pass
    

    
    
    
    mw.setUiElements()
    
    
    assert cb.isChecked() ==True
    assert not mw.btn_set.isEnabled()
    
    # mw.checkBox_look_for_other_os.setChecked(False)
    cb.setChecked(False)
    cb.clicked.emit()    
    
    assert cb.isChecked() ==False  

    assert mw.btn_set.isEnabled()
    
    qtbot.mouseClick(mw.btn_set, QtCore.Qt.LeftButton)
    assert mw.lbl_status.text() =="Waiting for authentication"
    
    while mw.lbl_status.text() =="Waiting for authentication":
        sleep(1)
    
    assert mw.lbl_status.text() =="Saving configurations"
    while  mw.lbl_status.text()=="Saving configurations":
        sleep(1)
        
        
 
    issues=[]
    assert main.get_value("GRUB_DISABLE_OS_PROBER=",issues)=="true"
    assert issues ==[]
    
    assert mw.lbl_status.text() =="Saved successfully"
    
    
    
    #repeat the same test but now the opposite case
    
    cb=mw.checkBox_look_for_other_os
    cb.setChecked(True)
    
    assert cb.isChecked() ==True  

    main.set_value("GRUB_DISABLE_OS_PROBER=","true")
    
    qtbot.mouseClick(mw.btn_set, QtCore.Qt.LeftButton)
    assert mw.lbl_status.text() =="Waiting for authentication"
    while mw.lbl_status.text()=='Waiting for authentication':
        sleep(1)
    assert mw.lbl_status.text() =="Saving configurations"
    
    while mw.lbl_status.text()=="Saving configurations":
        sleep(1)
        
        

    issues=[]
    assert main.get_value("GRUB_DISABLE_OS_PROBER=",issues)=="false"
    assert issues ==[]
            
    
    assert mw.lbl_status.text() =="Saved successfully"
    
def test_comboBox_configurations(qtbot):
    mw = main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)
    for i in range(len(mw.all_entries)):
        if i != mw.comboBox_grub_default.currentIndex():
            temp_entry = mw.all_entries[i]
            break
    
    
    snapshot_test="""GRUB_DEFAULT="""
    print(f' echo "{snapshot_test}" > {main.DATA_LOC}/snapshots/test_snapshot')
    subprocess.run([f' echo "{snapshot_test}" > {main.DATA_LOC}/snapshots/test_snapshot'],shell=True)
    main.set_value("GRUB_DEFAULT=",temp_entry,target_file=f"{main.DATA_LOC}/snapshots/test_snapshot")
    mw.setUiElements(only_snapshots=True)
    mw.comboBox_configurations.setCurrentIndex(mw.configurations.index("test_snapshot"))

    
    #check if the correct value for grub default was shown
    assert mw.all_entries[mw.comboBox_grub_default.currentIndex()] ==temp_entry
    
    
    
def test_btn_set(qtbot):
    mw = main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)
    assert "(modified)" not in mw.configurations[mw.comboBox_configurations.currentIndex()]
    old_ind=mw.comboBox_grub_default.currentIndex()
    
    curr_ind =change_comboBox_current_index(mw)
    print(curr_ind,"currentIndex")
    new_ind=mw.comboBox_grub_default.currentIndex()
    
    assert new_ind!=old_ind
    
    assert "(modified)" in mw.configurations[mw.comboBox_configurations.currentIndex()]
    qtbot.mouseClick(mw.btn_set, QtCore.Qt.LeftButton)
    
    with qtbot.waitSignal(mw.saveConfs_worker.signals.finished,raising=True,timeout=30*1000):
        pass
    
    assert mw.original_modifiers ==[]
    print(mw.configurations[mw.comboBox_configurations.currentIndex()])
    assert "(modified)" not in mw.configurations[mw.comboBox_configurations.currentIndex()]

def test_checkBox_look_for_other_os(qtbot):
    ''' Test if this comboBox defaults to not checked if GRUB_DISABLE_OS_PROBER wasn't found or commented ''' 
    mw=main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)

    test_config1="""#GRUB_DISABLE_OS_PROBER=false"""


    tmp_file=create_tmp_file(test_config1)
    issues=[]
    val =main.get_value("GRUB_DISABLE_OS_PROBER=",issues,tmp_file)
    assert val =="true"
    assert issues ==[f"GRUB_DISABLE_OS_PROBER= is commented out in {tmp_file}"]

def test_comboBox_grub_default_numbers(qtbot):
    mw = main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)
    
    test_config1="""GRUB_DEFAULT=\"1\""""
    
    sfile=create_snapshot(test_config1)
    mw.setUiElements(only_snapshots=True)
    mw.comboBox_configurations.setCurrentIndex(mw.configurations.index(sfile))
    
    assert mw.all_entries[mw.comboBox_grub_default.currentIndex()]==mw.all_entries[1]
    
    
    #todo test 0 >2
                #1 >2

def test_missing_double_quotes_default(qtbot):
    mw = main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)
    
    test_config="""GRUB_DEFAULT=Manjaro Linux
GRUB_TIMEOUT=20
GRUB_TIMEOUT_STYLE=menu
GRUB_DISTRIBUTOR=\"Manjaro\""""