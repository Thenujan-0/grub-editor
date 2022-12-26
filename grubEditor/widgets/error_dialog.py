from PyQt5 import QtWidgets ,uic,QtGui
from PyQt5.QtWidgets import QDesktopWidget,QApplication
import os 
import sys

PATH = os.path.dirname(os.path.realpath(__file__))



class ErrorDialogUi(QtWidgets.QDialog):
    """ Avaiable functions are
        set_error_title
        set_error_body
    
    """

    exitOnclose=False

    def __init__(self,):
        super(ErrorDialogUi,self).__init__()
        print(PATH)
        uic.loadUi(f'{PATH}/ui/error_dialog.ui',self)
        
        self.btn_ok.clicked.connect(self.selfClose)
        self.btn_copy.clicked.connect(self.onCopy)

        
        #make sure window is in center of the screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())


    def selfClose(self):
        self.close()
        
    def set_error_title(self,error_title):
        ''' Sets the title for error message dont use dot in the end as dot will be placed automatically
        '''
        
        #<p>An error has occured.Please consider reporting this to <span><a href="https://github.com/Thenujan-0/grub-editor/issues">github page</a></span></p>
        #is the main error message
        
        #only part thats going to be replaced is An error has occured
        
        text = self.lbl_error_title.text()
        self.lbl_error_title.setText(text.replace('An error has occured',error_title))
        
    def set_error_body(self,error_body):
        self.lbl_error_body.setText(error_body)
        
    def _exitApp(self):
        QApplication.exit()
    def exitOnAny(self):
        self.btn_ok.clicked.connect(self._exitApp)
        self.exitOnclose=True
    
    
    def closeEvent(self,event):
        if self.exitOnclose:
            self._exitApp()
        else:
            event.accept()
    
    def onCopy(self):
        QApplication.clipboard().setText(self.lbl_error_body.text())

def main():
    app= QtWidgets.QApplication([])
    window=ErrorDialogUi()
    
    try:
        window.set_error_title(sys.argv[1])
        window.set_error_body(sys.argv[2])
        
    except IndexError:
        pass
    window.show()
    app.setWindowIcon(QtGui.QIcon('/usr/share/pixmaps/grub-editor.png'))
    
    sys.exit(app.exec_())
    
    
if __name__ =="__main__":
    main()