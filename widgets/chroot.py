from PyQt5 import QtGui,QtCore,QtWidgets,uic
import sys
from time import sleep
import os
import subprocess





#removing the /widgets part of the string
PATH =os.path.dirname(os.path.realpath(__file__))[0:-8]
print(PATH)

HOME =os.getenv("HOME")

#to imports the widgets and libs
sys.path.append(PATH)

import widgets.progress as progress
from libs.worker import Worker , WorkerSignals
from widgets.dialog import DialogUi
from widgets.error_dialog import ErrorDialogUi




class CustomProgressUi(progress.ProgressUi):
    """ Parent window has to be set using the setParentWindow to make sure parent window  gets enabled when this window is closed """
    
    
    def setParentWindow(self,MainWindow):
        self.MainWindow=MainWindow
    def closeEvent(self,event):
        print('progress window is closing')
        self.MainWindow.setEnabled(True)
        event.accept()
        
class LoadingChrootUi(QtWidgets.QWidget):
    def __init__(self):
        super(LoadingChrootUi, self).__init__()
        uic.loadUi(f"{PATH}/ui/chroot_before.ui",self)

class ChrootUi(QtWidgets.QWidget):
    def __init__(self):
        super(ChrootUi, self).__init__()
        uic.loadUi(f"{PATH}/ui/chroot.ui",self)
        # self.show()
        
        
class ChrootAfterUi(QtWidgets.QWidget):

    def __init__(self,MainWindow):
        super(ChrootAfterUi, self).__init__()
        uic.loadUi(f"{PATH}/ui/chroot_after.ui",self)
        # self.show()
        self.threadpool=QtCore.QThreadPool()
        self.progress_window=None
        self.error_window=None
        self.MainWindow=MainWindow
        
        self.btn_reinstall_grub_package.clicked.connect(self.btn_reinstall_grub_package_callback)
        self.btn_exit_chroot.clicked.connect(self.btn_exit_chroot_callback)
        
    def onOutput(self,output):
        
        #! issue opening multiple progress windows at once can cause issues 
            if self.progress_window is not None:
                self.progress_window.update_lbl_details(output)
                
            elif self.error_window is not None:
                pass
                
            elif self.error_window is None:
                self.error_window=ErrorDialogUi()
                self.error_window.show()
                
                
    def btn_exit_chroot_callback(self):
        subprocess.run(['umount -a'],shell=True)
        
        
    def btn_reinstall_grub_package_callback(self):
        """ callback for btn_reinstall_grub_package 
            tries to reinstall grub package using pacman
        
        """
        
        
        #todo write tests to handle errors because of no  internet access error from pacman , pacman related errors etc
        
        def reinstall_grub_package(worker):
            p=subprocess.Popen([f'chroot /grub_editor_mount && pkexec pacman -S grub --noconfirm'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True)
            
            for line in p.stdout:
                sys.stdout.write(line.decode()+'reading from stdout')
                if "resolving dependencies..." in line.decode():
                    print('emitted started signal chroot.py ')
                    worker.signals.started.emit()
                worker.signals.output.emit(line.decode())
        
        #passing None as argument to set the worker to none at first and then change to the worker
        worker = Worker(reinstall_grub_package,worker=None)
        worker.kwargs['worker']=worker
        self.threadpool.start(worker)
        
        
        def show_loading():
            self.progress_window=CustomProgressUi()
            self.progress_window.lbl_status.setText('reinstalling grub package..')
            self.progress_window.show()
            self.MainWindow.setEnabled(False)
            self.progress_window.setParentWindow(self.MainWindow)
            
            #todo main window set enabled true when progress window is closed
            
            
        def btn_close_callback():
            self.progress_window.close()
            
        def onResult(result):
            #todo hide the loading window when process finishes
            
            if self.progress_window is not None: 
                self.progress_window.lbl_status.setText('Finished reinstalling grub package successfully')
                
                
                #remove the loading bar
                self.progress_window.verticalLayout.itemAt(1).widget().deleteLater()
                
                
                #add a close button
                self.btn_close= QtWidgets.QPushButton()
                self.btn_close.setText('Close')
                self.progress_window.verticalLayout.addWidget(self.btn_close)
                self.btn_close.clicked.connect(btn_close_callback)
            
        
                
            
    
        
                
        worker.signals.started.connect(show_loading)
        worker.signals.result.connect(onResult)
        worker.signals.output.connect(self.onOutput)
        


        
        
        
if __name__ == "__main__":
    app=QtWidgets.QApplication(sys.argv)
    window=ChrootUi()
    window.show()
    app.exec_()
