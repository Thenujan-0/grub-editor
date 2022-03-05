from PyQt5 import QtWidgets ,uic
from PyQt5.QtWidgets import QDesktopWidget
import os 

PATH = os.path.dirname(os.path.realpath(__file__))

class ErrorDialogUi(QtWidgets.QDialog):

    
    def __init__(self,):
        super(ErrorDialogUi,self).__init__()
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
        
    def set_error_title(self,error_title):
        ''' Sets the title for error message dont use dot in the end as dot will be placed automatically
        '''
        
        #<p>An error has occured.Please consider reporting this to <span><a href="https://github.com/Thenujan-0/grub-editor/issues">github page</a></span></p>
        #is the main error message
        
        #only part thats going to be replaced is An error has occured
        
        text = self.lbl_error_title.text()
        self.lbl_error_title.setText(text.replace('An error has occured',error_title))
        
    def set_error_title(self,error_body):
        self.lbl_error_body.setText(error_body)


def main():
    app= QtWidgets.QApplication([])
    window=ErrorDialogUi()
    window.show()
    app.exec_()
    
    
if __name__ =="__main__":
    main()