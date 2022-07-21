from PyQt5 import QtWidgets ,uic
from PyQt5.QtWidgets import QDesktopWidget,QApplication
import os 
import sys


#remove /widgets part from path
PATH = os.path.dirname(os.path.realpath(__file__))
PATH = PATH[0:-8]

sys.path.append(PATH)


class DialogUi(QtWidgets.QDialog):
    """ Create a dialog
    Available functions
    1.setText
    2.setBtnOkText
    3.exitOnAny (if you want to exit the app on closing the dialog or clicking ok or cancel)
    4.exitOnClose
    5.exitOnCancel
    
    """
    _exitOnclose=False
    
    def __init__(self,btn_cancel=True):
        super(DialogUi,self).__init__()
        uic.loadUi(f'{PATH}/ui/dialog.ui',self)
        if not btn_cancel:
            self.horizontalLayout.takeAt(0).widget().deleteLater()
        else:
            self.btn_cancel.clicked.connect(self._btn_cancel_callback)
        self.btn_ok.clicked.connect(self._btn_ok_callback)

        
        #make sure window is in center of the screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def _btn_ok_callback(self):
        self.close()

    def _btn_cancel_callback(self):
        self.close()
        
    def show_dialog(self):
        """ Decides on showing the dialog using the preferences file and the value of label that is set """
        
        self.show()
    
    def remove_btn_cancel(self):
        self.horizontalLayout.takeAt(0).widget().deleteLater()
        self.btn_cancel.setParent(None)
    
    def add_btn_cancel(self):
        self.btn_cancel=QtWidgets.QPushButton()
        self.btn_cancel.setText("Cancel")
        self.horizontalLayout.insertWidget(0,self.btn_cancel)
        self.btn_cancel.clicked.connect(self._btn_cancel_callback)

    def setText(self,text):
        self.label.setText(text)

    def setBtnOkText(self,text):
        self.btn_ok.setText(text)
        
    def removeCheckBox(self):
        self.checkBox.setParent(None)
        self.checkBox.deleteLater()
    
    def _exitApp(self):
        QApplication.quit()
    
    def exitOnAny(self):
        self.btn_ok.clicked.connect(self._exitApp)
        self.exitOnclose=True
        self.btn_cancel.clicked.connect(self._exitApp)
    
    def exitOnCancel(self):
        self.btn_cancel.clicked.connect(self._exitApp)
    
    def exitOnClose(self):
        self._exitOnClose=True
    
    def closeEvent(self,event):
        if self._exitOnclose:
            self._exitApp()
        else:
            event.accept()

def main():
    global PATH
    
    print(PATH)
    app = QtWidgets.QApplication([])
    window = DialogUi()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()