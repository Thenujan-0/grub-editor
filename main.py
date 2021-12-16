from PyQt5 import QtCore ,QtWidgets, uic
import sys
import subprocess
file_loc='/etc/default/grub'
import os
HOME =os.getenv('HOME')
subprocess.Popen([f'mkdir -p {HOME}/.grub_editor/snapshots'],shell=True)
from datetime import datetime as dt

#! has to be changed on release
write_file='/opt/grub_fake.txt'
def getValue(name):
    with open(file_loc) as file:
        data =file.read()
        start_index =data.find(name)
        end_index =data[start_index+len(name):].find('\n')+start_index+len(name)
        print('end_index',end_index)
        print(data[start_index+13:end_index])
        if start_index <0:
            return "None"
        else:
            if end_index <0:
                return data[start_index+13:]
            else:
                return data[start_index+13:end_index]


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
        self.ledit_grub_timeout.setText(getValue('GRUB_TIMEOUT='))
        self.createSnapshotList()
        self.btn_set.clicked.connect(self.btn_set_callback)
        
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
        setValue('GRUB_TIMEOUT=',self.ledit_grub_timeout.text())

    
    def viewCallbackCreator(self,arg):
        def func():
            global file_loc
            file_loc= f'{HOME}/.grub_editor/snapshots/'+arg
            self.ledit_grub_timeout.setText(getValue('GRUB_TIMEOUT='))
        return func
    
    def deleteCallbackCreator(self,arg):
        def func():
            subprocess.Popen([f'rm {HOME}/.grub_editor/snapshots/{arg}'],shell=True)
            self.ledit_grub_timeout.setText(getValue('GRUB_TIMEOUT='))
            self.createSnapshotList()
        return func
                
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
            #first number is 1
            number +=1
            
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
            self.HLayouts_list[-1].addWidget(self.pushButton_3)
            self.pushButton = QtWidgets.QPushButton(self.conf_snapshots)
            self.pushButton.setObjectName(f"btn_view{number}")
            self.pushButton.setText('view')
            self.pushButton.clicked.connect(self.viewCallbackCreator(line))
            self.HLayouts_list[-1].addWidget(self.pushButton)
            self.pushButton_3 = QtWidgets.QPushButton(self.conf_snapshots)
            self.pushButton_3.setObjectName(f"btn_delete{number}")
            self.pushButton_3.setText('delete')
            self.pushButton_3.clicked.connect(self.deleteCallbackCreator(line))
            self.HLayouts_list[-1].addWidget(self.pushButton_3)
            self.pushButton_2 = QtWidgets.QPushButton(self.conf_snapshots)
            self.pushButton_2.setObjectName(f"btn_set{number}")
            self.pushButton_2.setText('set')
            self.HLayouts_list[-1].addWidget(self.pushButton_2)
            
            
            self.VLayout_snapshot.addLayout(self.HLayouts_list[-1])
        
app =QtWidgets.QApplication(sys.argv)
window=Ui()
app.exec_()