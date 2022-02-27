from PyQt5 import QtWidgets ,uic
from PyQt5.QtWidgets import QDesktopWidget
import os 

PATH = os.path.dirname(os.path.realpath(__file__))

class DialogUi(QtWidgets.QDialog):
    def __init__(self,btn_cancel=True):
        super(DialogUi,self).__init__()
        uic.loadUi(f'{PATH}/ui/dialog.ui',self)
        if not btn_cancel:
            self.horizontalLayout.takeAt(0).widget().deleteLater()
        else:
            self.btn_cancel.clicked.connect(self.btn_cancel_callback)
        self.btn_ok.clicked.connect(self.btn_ok_callback)

        
        #make sure window is in center of the screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def btn_ok_callback(self):
        self.close()

    def btn_cancel_callback(self):
        self.close()
