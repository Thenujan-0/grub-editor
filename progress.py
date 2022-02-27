from PyQt5 import QtWidgets,QtCore,QtGui,uic
import sys
import os
import loading_bar

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
        if text =='Show details':
            self.scrollArea=QtWidgets.QScrollArea(self.centralwidget)
            self.scrollArea.setWidgetResizable(True)
            self.scrollAreaWidgetContents=QtWidgets.QWidget()
            self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 545, 110))
            self.gridLayout_2 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
            self.verticalLayout_2 = QtWidgets.QVBoxLayout()
            self.lbl_details = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            self.lbl_details.setWordWrap(True)
            self.update_lbl_details()
            
            self.verticalLayout_2.addWidget(self.lbl_details)
            self.gridLayout_2.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            self.verticalLayout.addWidget(self.scrollArea)
            # lbl =QtWidgets.QLabel(self.centralwidget)
            
            # self.verticalLayout.addWidget(lbl)
            
            btn.setText("Hide details")
            
        else:
            self.verticalLayout.itemAt(3).widget().deleteLater()
            self.lbl_details=None
            btn.setText("Show details")
    
    def update_lbl_details(self):
        ''' updates the lbl_details using the lbl_details_text if lbl_details is not None '''
        if self.lbl_details is not None:
            self.lbl_details.setText(self.lbl_details_text)
            
            
if __name__=="__main__":
    app = QtWidgets.QApplication([])
    window = ProgressUi()
    window.show()
    app.exec_()
    


