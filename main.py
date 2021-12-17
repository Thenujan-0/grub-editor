from PyQt5 import QtCore ,QtWidgets, uic
import sys
from functools import partial
import subprocess
import threading


file_loc='/etc/default/grub'
import os
HOME =os.getenv('HOME')
subprocess.Popen([f'mkdir -p {HOME}/.grub_editor/snapshots'],shell=True)
from datetime import datetime as dt
from time import sleep
#! has to be changed on release
write_file='/opt/grub_fake.txt'
def getValue(name):
    with open(file_loc) as file:
        print(file_loc,'file_loc')
        data =file.read()
        start_index =data.find(name)
        end_index =data[start_index+len(name):].find('\n')+start_index+len(name)
        print('end_index',end_index)
        print(data[start_index+len(name):end_index])
        if start_index <0:
            return "None"
        else:
            if end_index <0:
                return data[start_index+len(name):]
            else:
                return data[start_index+len(name):end_index]


def setValue(name,val):
    with open(file_loc) as file:
        data =file.read()
        start_index =data.find(name)
        end_index =data[start_index+13:].find('\n')+start_index+13
        data = data.replace(name+data[start_index+13:end_index],name+str(val))
    
    subprocess.Popen([f'mkdir -p {HOME}/.cache/grub_editor/'],shell=True)
    subprocess.Popen([f'touch {HOME}/.cache/grub_editor/grub.txt'],shell=True)
    with open(f'{HOME}/.cache/grub_editor/temp.txt','w') as file:
        file.write(data)
    subprocess.Popen([f'pkexec sh -c \' cp -f  "{HOME}/.cache/grub_editor/temp.txt"  '+write_file +' && sudo update-grub \' '],shell=True)



def clearLayout(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())
                
class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('main.ui',self)
        self.show()
        self.setUiElements()
        
        
    def setUiElements(self):
        self.ledit_grub_timeout.setText(getValue('GRUB_TIMEOUT='))
        
        if getValue('GRUB_TIMEOUT_STYLE=')=='hidden':
            self.comboBoxTimeoutStyle.setCurrentIndex(0)
        elif getValue('GRUB_TIMEOUT_STYLE=')=='menu':
            self.comboBoxTimeoutStyle.setCurrentIndex(1)
            
            
        self.createSnapshotList()
        self.btn_set.clicked.connect(self.btn_set_callback)
    
    def saveConfs(self):
        setValue('GRUB_TIMEOUT=',self.ledit_grub_timeout.text())
    
    def createSnapshot(self):
        with open(file_loc) as file:
            data= file.read()
        date_time =str(dt.now()).replace(' ','_')[:-7]
        print(date_time)
        subprocess.Popen([f'touch {HOME}/.grub_editor/snapshots/{date_time}'],shell=True)
        with open(f'{HOME}/.grub_editor/snapshots/{date_time}','w') as file:
            file.write(data)
        self.createSnapshotList()
    


    def btn_set_callback(self):
        self.saveConfs()

    def btn_rename_callback(self,number):
        pass
    def btn_view_callback(self,arg):
        global file_loc
        print(arg)
        file_loc= f'{HOME}/.grub_editor/snapshots/'+arg
        self.setUiElements()

        if self.verticalLayout.itemAt(3) is None:
            self.lbl_snapshot_view= QtWidgets.QLabel(self.edit_configurations)
            self.lbl_snapshot_view.setObjectName('lbl_snapshot_view')
            self.lbl_snapshot_view.setText('You are currently looking at snapshot from '+arg)
            self.verticalLayout.addWidget(self.lbl_snapshot_view)
            self.lbl_snapshot_view.setText('You are currently not 😎looking at snapshot from '+arg)
            
        else:
            self.verticalLayout.itemAt(3)
            self.lbl_snapshot_view.setText('You are currently looking at snapshot from '+arg)
                
    def set_btn_callback_creator(self,line):
        def funci(self):
            subprocess.run([f'pkexec cp -f  "{HOME}/.grub_editor/snapshots/{line}"  '+write_file],shell=True)
            subprocess.Popen([f'sudo update-grub'],shell=True)
        return funci
            
    def deleteCallbackCreator(self,arg):
        def func():
            string =f'rm {HOME}/.grub_editor/snapshots/{arg}'
            print(string)
            subprocess.Popen([f'rm {HOME}/.grub_editor/snapshots/{arg}'],shell=True)
            global file_loc
            print(file_loc,'file_loc after delete')
            print(f'{HOME}/.grub_editor/snapshots/{arg}','condition check string')
            if file_loc == f'{HOME}/.grub_editor/snapshots/{arg}':
                file_loc='/etc/default/grub'
                print(file_loc,'file_loc after delete and before set ui elems')
                print(self.verticalLayout.itemAt(3),'before if')
                print(self.verticalLayout.itemAt(3),'before if')
                print(self.verticalLayout.itemAt(3),'before if')
                if self.verticalLayout.itemAt(3):
                    print(self.verticalLayout.itemAt(3))
                    self.verticalLayout.itemAt(3).widget().deleteLater()
                    print(file_loc,'file_loc after delete and before set ui elems')
            self.setUiElements()
        return func
    def btn_rename_callback(self,number):
        btn = self.sender()
        if btn.text() == 'rename':
            self.ledit_ = QtWidgets.QLineEdit(self.conf_snapshots)
            self.ledit_.setObjectName("ledit_")
            self.targetLabel=self.HLayouts_list[number].itemAt(0).widget()
            print(number)
            print(self.targetLabel)
            btn.parent().layout().replaceWidget(self.targetLabel,self.ledit_)
            self.targetLabel.deleteLater()
            btn.setText('set name')
        else:
            pass
        
        
        
               
    def createSnapshotList(self):
        contents = subprocess.check_output([f'ls {HOME}/.grub_editor/snapshots/'],shell=True).decode()
        print(contents)
        lines =contents.splitlines()

        self.HLayouts_list=[]
        number =0
        clearLayout(self.VLayout_snapshot)
        self.btn_create_snapshot = QtWidgets.QPushButton(self.conf_snapshots)
        self.btn_create_snapshot.setObjectName("btn_create_snapshot")
        self.btn_create_snapshot.setText("create a snapshot now")
        self.btn_create_snapshot.clicked.connect(self.createSnapshot)
        self.VLayout_snapshot.addWidget(self.btn_create_snapshot)
        for line in lines:
            #first number is 0
            
            self.HLayouts_list.append(QtWidgets.QHBoxLayout())
            self.HLayouts_list[-1].setObjectName(f'HLayout_snapshot{number}')
            
            #!needs change variables cannot be used
            self.lineEdit = QtWidgets.QLabel(self.conf_snapshots)
            self.lineEdit.setObjectName(f"lbl_snapshot{number}")
            self.lineEdit.setText(line)
            self.HLayouts_list[-1].addWidget(self.lineEdit)
            self.pushButton_3 = QtWidgets.QPushButton(self.conf_snapshots)
            self.pushButton_3.setObjectName(f"btn_rename{number}")
            self.pushButton_3.setText('rename')
            self.pushButton_3.clicked.connect(partial(self.btn_rename_callback,number))
            self.HLayouts_list[-1].addWidget(self.pushButton_3)
            self.pushButton = QtWidgets.QPushButton(self.conf_snapshots)
            self.pushButton.setObjectName(f"btn_view{number}")
            self.pushButton.setText('view')
            self.pushButton.clicked.connect(partial(self.btn_view_callback,line))
            self.HLayouts_list[-1].addWidget(self.pushButton)
            self.pushButton_3 = QtWidgets.QPushButton(self.conf_snapshots)
            self.pushButton_3.setObjectName(f"btn_delete{number}")
            self.pushButton_3.setText('delete')
            self.pushButton_3.clicked.connect(self.deleteCallbackCreator(line))
            self.HLayouts_list[-1].addWidget(self.pushButton_3)
            self.pushButton_2 = QtWidgets.QPushButton(self.conf_snapshots)
            self.pushButton_2.setObjectName(f"btn_set{number}")
            self.pushButton_2.setText('set')
            self.pushButton_2.clicked.connect(self.set_btn_callback_creator(line))
            self.HLayouts_list[-1].addWidget(self.pushButton_2)
            
            # print(self.VLayout_snapshot)
            self.VLayout_snapshot.addLayout(self.HLayouts_list[-1])
            
            #first number is 0
            
            number +=1

app =QtWidgets.QApplication(sys.argv)
window=Ui()
app.exec_()