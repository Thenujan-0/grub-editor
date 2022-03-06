import sys
import os;
from PyQt5 import QtWidgets,QtCore
import traceback
from time import sleep
PATH=os.path.dirname(os.path.realpath(__file__))
#/home/thenujan/Desktop/Code/grub-editor/
PATH=PATH[0:-6]




#include parent directory 
sys.path.append(PATH)

from  widgets.progress import ProgressUi
from tests.test_functions import TestFunctions
from libs.worker import Worker,WorkerSignals
import unittest



class CustomWorkerSignals(WorkerSignals):
    ''' contains some signals specific to the ProgressUi '''
    update_lbl_details=QtCore.pyqtSignal(str)






class CustomTestCase(unittest.TestCase):
    def assertWidget(self,type:str,widget):
        ''' First arg is the type of widget it should be a string 
            Second arg is the Actual widget to check 
        '''
        self.assertIn(type,widget.__str__())
        



class TestProgress(ProgressUi,TestFunctions):
    
    def __init__(self,unittest_obj,run_string):
        super().__init__()
        self.threadpool= QtCore.QThreadPool()
        # self.startWorker()
        exec(run_string)
        self.utest=unittest_obj
        
        
    def test_btn_show_details(self,worker):
        sleep(2)
        
        vcount  =self.verticalLayout.count()
        btn_show_details =self.verticalLayout.itemAt(vcount-1).widget()
        
        #check if the last widget is push button
        self.utest.assertWidget("QPushButton",btn_show_details)
        self.utest.assertEqual("Show details",btn_show_details.text())
        
        
        print("Clicked THE SHOW DETAILS BUTTON")
        worker.signals.click_button.emit(self.btn_show_details)
        
        sleep(1)
        vcount  =self.verticalLayout.count()
        print(vcount)
        #check if last widget is QScrolArea
        self.utest.assertIn('QScrollArea' , self.verticalLayout.itemAt(vcount-1).widget().__str__())
        sleep(1)
        
        self.utest.assertEqual('Hide details',btn_show_details.text())
        
        print("Clicked THE HIDE DETAILS BUTTON ")
        worker.signals.click_button.emit(self.btn_show_details)
        sleep(2)
        
        
        #add a close button to the widget
        
        worker.signals.exec_str.emit("""
self.btn_close= QtWidgets.QPushButton()
self.btn_close.setText("Close")
self.verticalLayout.addWidget(self.btn_close)
        """)
        print("added a close button")
        
        sleep(2)
        
        worker.signals.click_button.emit(self.btn_show_details)
        sleep(2)
        print('Clicked show details')
        
        vcount  =self.verticalLayout.count()
        print(vcount,"vcount")
        #check if thw widget before last widget is QScrolArea
        self.utest.assertIn('QScrollArea' , self.verticalLayout.itemAt(vcount-2).widget().__str__())
        sleep(1)
        
        
        worker.signals.click_button.emit(self.btn_show_details)
        print("clicked Hide details")
        sleep(2)
        
        worker.signals.quit_app.emit()
        # sleep(1)
        
        
        
        
        
        
        #updating label
        
    def test_update_lbl_details(self):
        pass
        
    def startWorker(self,function):
        
            
        #passing None as argument to set worker to None so i can set it to worker in 
        # the following step
        worker =Worker(function,worker=None)
        worker.kwargs['worker']=worker
        
        
        self.threadpool.start(worker)
        worker.signals.click_button.connect(self.click_button)
        worker.signals.quit_app.connect(self.quit_app)
        worker.signals.finished.connect(self.worker_finished)
        worker.signals.exec_str.connect(self.exec_str)
        
    def worker_finished(self):
        print('worker finished')
        
    
    
    def quit_app(self):
        app.quit()
    
    
    
    def exec_str(self,string):
        try:
            exec(string)
        except Exception as e:
            print(traceback.format_exc())
            print('The string that was executed wil now be printed')
            print(string)
        
        
        
        
        
def main(unittest_obj,run_string):
    global app;
    app = QtWidgets.QApplication([])
    global window;
    window = TestProgress(unittest_obj,run_string)
    window.show()
    app.exec_()
        
    
        
        
class UnitTest_(CustomTestCase):
    def test_btn_show_details(self):
        main(self,"self.startWorker(self.test_btn_show_details)")
    
    def test_lbl_details(self):
        main(self,'')

if __name__ == '__main__':
    unittest.main()








