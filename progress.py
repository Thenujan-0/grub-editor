from PyQt5 import QtWidgets,QtCore,QtGui,uic
import sys
import os


class ProgressUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'ui/progress.ui',self)


if __name__=="__main__":
    app = QtWidgets.QApplication([])
    window = ProgressUi()
    window.show()
    app.exec_()
    


