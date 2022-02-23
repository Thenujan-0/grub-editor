from PyQt5 import QtGui,QtCore,QtWidgets,uic
import sys
from time import sleep
import os
import subprocess
import progress

PATH =os.path.dirname(os.path.realpath(__file__))
print(PATH)
class ChrootUi(QtWidgets.QWidget):
    def __init__(self):
        super(ChrootUi, self).__init__()
        uic.loadUi(f"{PATH}/ui/chroot.ui",self)
        # self.show()
class ChrootAfterUi(QtWidgets.QWidget):
    def __init__(self):
        super(ChrootAfterUi, self).__init__()
        uic.loadUi(f"{PATH}/ui/chroot_after.ui",self)
        # self.show()
        
    def btn_reinstall_grub_package_callback(self):
        """ callback for btn_reinstall_grub_package 
            tries to reinstall grub package using pacman
        
        """
        # subprocess.run([''])
        self.progress_window=progress.ProgressUi()

if __name__ == "__main__":
    app=QtWidgets.QApplication(sys.argv)
    window=ChrootUi()
    window.show()
    app.exec_()
