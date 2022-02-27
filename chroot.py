from PyQt5 import QtGui,QtCore,QtWidgets,uic
import sys
from time import sleep
import os
import subprocess
import progress
from worker import Worker , WorkerSignals
from dialog import DialogUi


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
        self.threadpool=QtCore.QThreadPool()
        self.progress_window=None
        
        
        
        self.btn_reinstall_grub_package.clicked.connect(self.btn_reinstall_grub_package_callback)
        
    def btn_reinstall_grub_package_callback(self):
        """ callback for btn_reinstall_grub_package 
            tries to reinstall grub package using pacman
        
        """
        #todo check if there is internet access
        
        def reinstall_grub_package(worker):
            p=subprocess.Popen(['pkexec pacman -S grubas --noconfirm'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True)
            
            for line in p.stdout:
                sys.stdout.write(line.decode()+'reading from stdout')
                if "resolving dependencies..." in line.decode():
                    worker.signals.started.emit()
                worker.signals.output.emit(line.decode())
        
        #passing None as argument to set the worker to none at first and then change to the worker
        worker = Worker(reinstall_grub_package,worker=None)
        worker.kwargs['worker']=worker
        self.threadpool.start(worker)
        
        
        def show_loading():
            self.progress_window=progress.ProgressUi()
            self.progress_window.lbl_status.setText('reinstalling grub package..')
            self.progress_window.show()
            
        def error_handler():
            print('recieved error')
            self.reinstall_grub_package_error_dialog=DialogUi()
            self.reinstall_grub_package_error_dialog.label.setText('An error occured while installing')
            self.reinstall_grub_package_error_dialog.show()
            
        def btn_close_callback():
            self.close()
            
        def onResult(result):
            ''' hide the loading window when process finishes '''
            if self.progress_window is not None: 
                self.progress_window.lbl_status.setText('Finished reinstalling grub package successfully')
                
                
                #remove the loading bar
                self.progress_window.verticalLayout.itemAt(1).widget().deleteLater()
                
                
                #add a close button
                self.btn_close= QtWidgets.QPushButton()
                self.btn_close.setText('Close')
                self.verticalLayout.addWidget(self.btn_close)
                self.btn_close.clicked.connect(btn_close_callback)
    
        
                
        worker.signals.started.connect(show_loading)
        worker.signals.error.connect(error_handler)
        worker.signals.result.connect(onResult)
        worker.signals.output.connect(self.update_lbl_details)
        

        
    def update_lbl_details(self,text:str):
        ''' updates the lbl_details adds the the string to the pre existing string in lbl_details '''
        pre_text=self.progress_window.lbl_details_text
        
        self.progress_window.lbl_details_text = pre_text+text
        self.progress_window.update_lbl_details()
        
        
        
if __name__ == "__main__":
    app=QtWidgets.QApplication(sys.argv)
    window=ChrootUi()
    window.show()
    app.exec_()
