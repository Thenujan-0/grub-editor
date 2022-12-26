import sys
import os

from PyQt5 import QtWidgets,QtCore


PATH= os.path.dirname(os.path.realpath(__file__))


if 'widgets' == PATH[-7:]:
    print(PATH[0:-8])
    sys.path.append(PATH[0:-8])
    
import widgets.loading_bar as loading_bar
from grubEditor.libs.qt_functools import insert_into


class ProgressUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
    

        self.centralwidget=QtWidgets.QWidget(self)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.verticalLayout=QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(-1, -1, -1, 30)
        self.lbl_status=QtWidgets.QLabel(self.centralwidget)
        self.lbl_status.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_status.setText("please wait")
        self.verticalLayout.addWidget(self.lbl_status)
        self.gridLayout.addLayout(self.verticalLayout,0,0,1,1)
        self.setCentralWidget(self.centralwidget)
        self.loading_bar=loading_bar.LoadingBar()
        self.loading_bar.setMinimumHeight(20)
        self.verticalLayout.addWidget(self.loading_bar)
        
        self.btn_show_details=QtWidgets.QPushButton(self.centralwidget)
        self.btn_show_details.setText("Show details")
        self.verticalLayout.addWidget(self.btn_show_details)
        
        
        self.resize(400,200)
        
        
        self.lbl_details_text=''
        self.lbl_details=None
        
        self.btn_show_details.clicked.connect(self.btn_show_details_callback)

        

        
    def btn_show_details_callback(self):
        btn=self.sender()
        text =btn.text()
        if self.verticalLayout.itemAt(3) is not None:
            print(self.verticalLayout.itemAt(3).widget())
        else:
            print(None)
        if text =='Show details':
            self.scrollArea=QtWidgets.QScrollArea(self.centralwidget)
            self.scrollArea.setWidgetResizable(True)
            self.scrollAreaWidgetContents=QtWidgets.QWidget()
            self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 545, 110))
            self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
            self.verticalLayout_2 = QtWidgets.QVBoxLayout()
            self.lbl_details = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            self.lbl_details.setWordWrap(True)
            
            self.lbl_details.setText(self.lbl_details_text)
            
            #find the index of the button
            for index in range(self.verticalLayout.count()):
                item = self.verticalLayout.itemAt(index).widget()
                if 'QPushButton' in item.__str__() and item.text()=='Show details':
                    
                    self.verticalLayout_2.addWidget(self.lbl_details)
                    self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
                    self.scrollArea.setWidget(self.scrollAreaWidgetContents)
                    
                    # if it is the last widget of the veritical layout
                    if self.verticalLayout.count()-1 == index:
                        
                        self.verticalLayout.addWidget(self.scrollArea)
                        
                    #if it isnt the last widget of the verticalLayout
                    else:
                        insert_into(self.verticalLayout,index+1,self.scrollArea)
                        break
                    
                    
            # lbl =QtWidgets.QLabel(self.centralwidget)
            
            # self.verticalLayout.addWidget(lbl)
            
            btn.setText("Hide details")
            
        elif text=='Hide details':
            self.lbl_details=None
            btn.setText("Show details")
            for index in range(self.verticalLayout.count()):
                item = self.verticalLayout.itemAt(index).widget()
                if 'QScrollArea' in item.__str__():
                    item.deleteLater()
                    item.setParent(None)
                    #delete the child widget of the QScrollArea
                    item.widget().deleteLater()
                    break
        else:
            print("unknown text in btn_show_details")            
    
    def update_lbl_details(self,text:str):
        ''' updates the lbl_details adds the the string to the pre existing string in lbl_details
            This doesnt add new lines
        '''
        
        pre_text=self.lbl_details_text
        self.lbl_details_text=pre_text+text
        
        if self.lbl_details is not None:
            self.lbl_details.setText(self.lbl_details_text)
            
            
if __name__=="__main__":
    global APP
    APP = QtWidgets.QApplication([])
    
    window = ProgressUi()
    window.show()
    APP.exec_()
    


