
import subprocess
from time import sleep

from PyQt5 import QtCore

from grubEditor import main
from grubEditor.libs import find_entries



def test_grub_cfg_not_found(qtbot):
    
    #change the GRUB_CONF to a non-existing file so that not found error will be raised
    find_entries.GRUB_CONF_NONEDITABLE="/boot/grub/grub1.cfg"
    
    
    
    mw=main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)
    
    assert mw.dialog_grub_cfg_not_found.isVisible()
    
    find_entries.GRUB_CONF="/boot/grub/grub.cfg"
    
    qtbot.mouseClick(mw.dialog_grub_cfg_not_found.btn_ok, QtCore.Qt.LeftButton)
    
    assert not mw.dialog_grub_cfg_not_found.isVisible()
    
    
    
def test_grub_cfg_permission(qtbot):
    
    subprocess.run(['pkexec chmod 600 /boot/grub/grub.cfg'],shell=True)
    
    mw=main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)
    
    assert mw.dialog_cfg_permission.isVisible()
    
    subprocess.run(['pkexec chmod 644 /boot/grub/grub.cfg'],shell=True)
    
    
        
