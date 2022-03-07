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
    
    
    #this will be emited with the name of the next function to call when a test case finishes
    function_finished=QtCore.pyqtSignal(str)

class CustomWorker(Worker):
    def __init__(self,fn,*args,**kwargs):
        super().__init__(fn,*args,**kwargs)
        
        self.signals=CustomWorkerSignals()



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
        sleep(1)
        
        #add a close button to the widget
        
        worker.signals.exec_str.emit("""
self.btn_close= QtWidgets.QPushButton()
self.btn_close.setText("Close")
self.verticalLayout.addWidget(self.btn_close)
        """)
        print("added a close button")
        
        
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
        
        worker.signals.function_finished.emit("test_update_lbl_details")
        
        # worker.signals.quit_app.emit()
        # sleep(1)
        
        
        
        
        
        
        #updating label
        
    def test_update_lbl_details(self,worker):
        print('test_update_lbl_details has started')
        sleep(2)
        str1="assume that this is a big line of text from console ouput"
        worker.signals.update_lbl_details.emit(str1)
        sleep(1)
        
        print("checking  if lbl_details_text contains the right text")
        self.utest.assertEqual(self.lbl_details_text,str1)
        
        print("clicked btn_show_details")
        self.click_button(self.btn_show_details)
        
        sleep(1)
        
        print('Checking if lbl_details is now showing the right string')
        self.utest.assertEqual(self.lbl_details.text(),str1)
        
        str2="\nThis is Another big text"
        worker.signals.update_lbl_details.emit(str2)
        
        sleep(1)
        print("check if the lbl_details now shows the correct string")
        self.utest.assertEqual(str1+str2,self.lbl_details.text())
        
        
        print("checking if clicking hide details and then show details cause any issues in lbl_details text")
        self.click_button(self.btn_show_details)
        sleep(1)
        self.click_button(self.btn_show_details)
        sleep(1)
        self.utest.assertEqual(self.lbl_details.text(),str1+str2)
        
        
        worker.signals.quit_app.emit()
        
        
    def function_finished_callback(self,name_next_fn):
        print('function_finished_callback was called')
        exec_str="self.startWorker(self."+name_next_fn+")"
        print(exec_str)
        exec(exec_str)
        
    def startWorker(self,function):
        
            
        #passing None as argument to set worker to None so i can set it to worker in 
        # the following step
        worker =CustomWorker(function,worker=None)
        worker.kwargs['worker']=worker
        
        
        self.threadpool.start(worker)
        worker.signals.click_button.connect(self.click_button)
        worker.signals.quit_app.connect(self.quit_app)
        worker.signals.finished.connect(self.worker_finished)
        worker.signals.exec_str.connect(self.exec_str)
        # print(type(worker.signals),'my custom signal')
        worker.signals.update_lbl_details.connect(self.update_lbl_details)
        # worker.signals.function_finished.connect(self.function_finished_callback)
        
        
    def worker_finished(self):
        print('worker finished')
        sleep(5)
        app.quit()
        # self.close()
        # print('done')
        # sys.exit(app.exec_)
    
    
    def quit_app(self):
        pass    
    
    
    def exec_str(self,string):
        try:
            exec(string)
        except Exception as e:
            print(traceback.format_exc())
            print('The string that was executed wil now be printed')
            print(string)
        
        
        
        
        
def main(unittest_obj,run_string):
    global app;
    app = QtWidgets.QApplication(sys.argv)
    global window;
    window = TestProgress(unittest_obj,run_string)
    window.show()
    app.exec_()
        
    
        
        
class UnitTest_(CustomTestCase):
    def test_btn_show_details(self):
        main(self,"self.startWorker(self.test_btn_show_details)")
    
    def test_lbl_details(self):
        print('started second test')
        self.assertEqual(1,1)
        # main(self,'self.startWorker(self.test_update_lbl_details)')

if __name__ == '__main__':
    unittest.main()








