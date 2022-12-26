#!/usr/bin/python


import sys
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont,QPalette,QPolygonF,QBrush
from PyQt5.QtCore import Qt , QPointF,QRectF,QObject,pyqtSignal,QRunnable,pyqtSlot,QThreadPool,QTimer
import traceback
from time import sleep



class WorkerSignals(QObject):
    """ defines the signals available from a running worker thread 
    
    supported signals are:
    finished 
        No data
    
    error 
        tuple( exctype ,value ,traceback.format_exc() )
    
    result 
        object data returned from processing , anything
    
    
    """
    
    finished = pyqtSignal()
    error= pyqtSignal(tuple)
    result = pyqtSignal(object)
    
class Worker(QRunnable):
    """ 
    Worker thread 
    inherits from QRunnable to handler worker thread setup , signals, wrap-up.
    :param callback: The function to run on this worker thread . Supllied args and
                kwargs will be passed through the runner
    :type callback: function
    :param args : Arguments to pass the callback function
    :param kwargs : keyword to pass to the callback function
    
    """
    
    def __init__(self,fn,*args,**kwargs):
        super(Worker, self).__init__()
        self.fn =fn
        self.args= args
        self.kwargs=kwargs
        self.signals=WorkerSignals()
    
    
    @pyqtSlot()
    def run(self):
        """ 
        initialise the runner function with passed args and kwargs
        """
        
        try:
            result =self.fn(*self.args,**self.kwargs)
        
        except:
            traceback.print_exc()
            exctype,value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc() ))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
    
    

class LoadingBar(QWidget):

    def __init__(self):
        super().__init__()
        self.threadpool=QThreadPool()

        self.initUI()
        
        #position of colored part in loading bar 0 -100
        self.position=20
        self.startWorker(self.move_loading_bar)
        self.loading_increasing=True
        
        
        # self.timer=QTimer()
        # self.timer.timeout.connect(self.move_loading_bar)
        # self.timer.start(500)
    
    def move_loading_bar(self):
        """ move the loading bar back and forth by changing the value of self.position """
        while True:
            # print('moving loading bar',self.position)
            sleep(0.015)
            if self.position ==100:
                self.loading_increasing=False
            elif self.position==0:
                self.loading_increasing=True
            
            if self.loading_increasing:
                self.position+=1
            else:
                self.position-=1

            qp=QPainter()
            
            #Error might occur if the LoadingBar widget is deleted so to catch that
            try:
                self.update()
            except RuntimeError:
                pass
        
    
    def startWorker(self,fn,*args,**kwargs):
        worker= Worker(fn)
        
        self.threadpool.start(worker)
        
        
    def initUI(self):


        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('loading please wait')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        
        width = self.width()
        height = self.height()
        
        self.widget_height= 6
        
        
        #the part of the loading bar that is not going to have the progressed part
        reduce_amount = width*0.6
        
        top_left =QPointF(int(width*0.1),int(height/2-self.widget_height/2))
        bottom_right =QPointF(int(width*0.9)-reduce_amount ,int(height/2 +self.widget_height/2))
        
        bigger_bottom_right =QPointF(int(width*0.9) ,int(height/2+self.widget_height/2) )
        
        recty =QRectF(QPointF(top_left.x()+self.position/100*reduce_amount,top_left.y()),
                      QPointF(bottom_right.x()+self.position/100*reduce_amount,bottom_right.y()))
        bigger_recty=QRectF(top_left,bigger_bottom_right)
        
        
        #non progressed part (bigger rounded rect)
        qp.setPen(QPalette().color(QPalette.Disabled,QPalette.Text))
        qp.setBrush(QBrush(QPalette().color(QPalette.Active,QPalette.Button)))
        qp.drawRoundedRect(bigger_recty,3,3)        
        
        
        #progressed part
        qp.setBrush(QBrush(QPalette().color(QPalette().Inactive,QPalette().Highlight)))
        qp.setPen(QPalette().color(QPalette().Active,QPalette().Highlight))
        qp.drawRoundedRect(recty,2,2)


def main():

    app = QApplication(sys.argv)
    ex = LoadingBar()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()