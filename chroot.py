from PyQt5 import QtGui,QtCore,QtWidgets,uic
import sys
from time import sleep
import os


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
        

if __name__ == "__main__":
    app=QtWidgets.QApplication(sys.argv)
    window=ChrootUi()
    window.show()
    app.exec_()
