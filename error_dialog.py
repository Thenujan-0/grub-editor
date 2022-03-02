from PyQt5 import QtWidgets ,uic
from PyQt5.QtWidgets import QDesktopWidget
import os 

PATH = os.path.dirname(os.path.realpath(__file__))

class DialogUi(QtWidgets.QDialog):
    def __init__(self,):
        super(DialogUi,self).__init__()
        uic.loadUi(f'{PATH}/ui/error_dialog.ui',self)
        
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


def main():
    app= QtWidgets.QApplication([])
    window=DialogUi()
    window.show()
    app.exec_()
    
    
if __name__ =="__main__":
    main()