#!/usr/bin/python
from PyQt5 import QtCore ,QtWidgets, uic,QtGui
import sys
from functools import partial
import subprocess
import threading
from datetime import datetime as dt
from time import sleep
import os
from subprocess import PIPE, Popen
from time import perf_counter
import traceback
file_loc='/etc/default/grub'



write_file='/opt/grub_fake.txt'
write_file=file_loc

HOME =os.getenv('HOME')
PATH = os.path.dirname(os.path.realpath(__file__))
to_write_data=None


subprocess.Popen([f'mkdir -p {HOME}/.grub_editor/snapshots'],shell=True)

def getValue(name):
    with open(file_loc) as file:
        data =file.read()
        start_index =data.find(name)
        end_index =data[start_index+len(name):].find('\n')+start_index+len(name)
        if start_index <0:
            return "None"
        else:
            if end_index <0:
                return data[start_index+len(name):]
            else:
                return data[start_index+len(name):end_index]


def setValue(name,val):
    global to_write_data
    if to_write_data is None:
        with open(file_loc) as file:
            to_write_data =file.read()
    
    start_index =to_write_data.find(name)
    end_index =to_write_data[start_index+len(name):].find('\n')+start_index+len(name)
    
    to_write_data = to_write_data.replace(name+to_write_data[start_index+len(name):end_index],name+str(val))
    
    subprocess.Popen([f'mkdir -p {HOME}/.cache/grub_editor/'],shell=True)
    subprocess.Popen([f'touch {HOME}/.cache/grub_editor/grub.txt'],shell=True)
    with open(f'{HOME}/.cache/grub_editor/temp.txt','w') as file:
        file.write(to_write_data)



def clearLayout(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())

class WorkerSignals(QtCore.QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)

   
class Worker(QtCore.QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @QtCore.pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
                    
class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        self.threadpool= QtCore.QThreadPool()
        uic.loadUi(f'{PATH}/main1.ui',self)
        self.show()
        
        #dictionary to store qlineEdits for rename .stored widget is qlineEditWidget. key is index of the row
        self.rename_line_edits={}
        
        #dictionary for storing labels (rename) . key is index of the row
        self.btn_set.clicked.connect(self.btn_set_callback)
        self.rename_labels={}
        self.ledit_grub_timeout.setValidator(QtGui.QDoubleValidator())
        
        
        
        #load the entries
        import find_entries
        self.main_entries = find_entries.main_entries

        self.all_entries =[]
        for entry in self.main_entries:
            if len(entry.sub_entries) ==0:
                self.comboBox_grub_default.addItem(entry.title)
                self.all_entries.append(entry.title)
            else:
                for sub in entry.sub_entries:
                    self.comboBox_grub_default.addItem(sub.parent.title+' >'+sub.title)
                    self.all_entries.append(sub.parent.title+' >'+sub.title)
        print(self.all_entries)
        self.setUiElements()
        
        #label that shows saving or saved sucessfully
        self.lbl_details=None
        
        #variable to store the execution output  when saving
        self.lbl_details_text=''
        
        
        
    def setUiElements(self,no_snapshot=False):
        """reloads the ui elements that should be reloaded"""
        self.ledit_grub_timeout.setText(getValue('GRUB_TIMEOUT='))
        
        if getValue('GRUB_TIMEOUT_STYLE=')=='hidden':
            self.checkBox_show_menu.setChecked(False)
        elif getValue('GRUB_TIMEOUT_STYLE=')=='menu':
            self.checkBox_show_menu.setChecked(True)
        grub_default_val =getValue('GRUB_DEFAULT=')
        if grub_default_val[0]=='"':
            grub_default_val= grub_default_val[1:]
        if grub_default_val[-1]=='"':
            grub_default_val=grub_default_val[:-1]
            
        
            
        if grub_default_val=='saved':
            self.previously_booted_entry.setChecked(True)
            # self.comboBox_grub_default.setCurrentIndex(0)
        else:
            self.predefined.setChecked(True)
            # self.comboBox_grub_default.setCurrentIndex(self.all_entries.index(grub_default_val))
            
            
        if getValue('GRUB_TIMEOUT=')=='-1':
            self.checkBox_boot_default_entry_after.setChecked(False)
        else:
            self.checkBox_boot_default_entry_after.setChecked(True)
            
        self.createSnapshotList()
        
        
    def set_lbl_details(self):
        """receives the string in lbl_details_text and sets it as the label for lbl_details"""
        try:
            self.lbl_details.setText(self.lbl_details_text)
        except:
            #this could fail because of two reasons 
            #1.lbl_details hasnt yet been created
            #2.it was deleted
            pass
        
        
    def saveConfs(self):
        
        # reset the string
        self.lbl_details_text=''
        
        
        if self.checkBox_show_menu.isChecked():
            setValue('GRUB_TIMEOUT_STYLE=','menu')
        else:
            setValue('GRUB_TIMEOUT_STYLE=','hidden')
        
        self.grub_default =str(self.comboBox_grub_default.currentText())
        if self.grub_default.count('>') <=1:
            pass
            if '>' in self.grub_default:
                front_part=self.grub_default[:self.grub_default.find(' >')]
                last_part=self.grub_default[self.grub_default.find('>'):]
                to_write='"'+front_part+last_part+'"'
                setValue('GRUB_DEFAULT=',to_write)
                print(to_write+'part to be written')
            else:
                setValue('GRUB_DEFAULT=','\"'+self.grub_default+'\"')
            #set the value of grub_default
        else:
            print('Error occured when setting grub default as combobox text has more than one  1\' >\'  ')
            print(self.grub_default)
            
        if self.checkBox_boot_default_entry_after.isChecked():
            setValue('GRUB_TIMEOUT=',self.ledit_grub_timeout.text())
        else:
            setValue('GRUB_TIMEOUT=','-1')
        def final(self):
            try:
                
                
                #! todo find a way to show an error message if something goes wrong 
                process = subprocess.Popen([f' pkexec sh -c \'echo \"authentication completed\"  && cp -f  "{HOME}/.cache/grub_editor/temp.txt"  '+write_file +' && sudo update-grub 2>&1 \'  '], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
                self.lbl_details_text='Waiting for authentication \n'
                
                self.set_lbl_details()
                
                self.lbl_status.setText('Waiting for authentication')
                # out = process.communicate()[0].decode()
                # if self.lbl_details is not None:
                #     print('setting')
                #     print(out,'out')
                #     self.lbl_details.setText(out)
                # self.lbl_status.setText('Saved successfully')
                while True:
                    authentication_complete=False
                    authentication_error=False
                    for line in process.stdout:
                        if not authentication_complete:
                            self.lbl_status.setText('Saving configurations')
                            authentication_complete=True
                        sys.stdout.write(line.decode())
                        if 'Error executing command as another user: Not authorized' in line.decode():
                            authentication_error=True
                        self.lbl_details_text= self.lbl_details_text+ line.decode()
                        
                        #this handles the case where lbldetails hasnt yet been created
                        if self.lbl_details is not None:
                            
                            #this handles the case where lbl_details_text gets deleted after once its been created
                            try:
                                self.lbl_details.setText(self.lbl_details_text)
                            except:
                                pass
                    break

                    if self.lbl_details is not None:
                        for line in process.stdout:
                            sys.stdout.write(line.decode())
                            try:
                                last = self.lbl_details.text()
                                print('last is ',last)
                                self.lbl_details.setText(last+line.decode())
                            except:
                                #! todo 
                                print('looks like label was deleted')
                            
                        break
                if not authentication_error:
                    self.lbl_status.setText('Saved successfully')
                else:
                    self.lbl_status.setText('Authentication error occured')
                    self.lbl_status.setStyleSheet('color: red')
                        
            except Exception as e:
                print(e)
                print('error trying to save the configurations')
                self.lbl_status.setText('An error occured when saving')
                self.lbl_status.setStyleSheet('color: red')
        threading.Thread(target=final,args=[self]).start()

        
        
        
    def createSnapshot(self):
        with open(file_loc) as file:
            data= file.read()
        date_time =str(dt.now()).replace(' ','_')[:-7]
        subprocess.Popen([f'touch {HOME}/.grub_editor/snapshots/{date_time}'],shell=True)
        with open(f'{HOME}/.grub_editor/snapshots/{date_time}','w') as file:
            file.write(data)
        self.createSnapshotList()
    


    def btn_show_details_callback(self,tab):
        print(self.verticalLayout_2.itemAt(1))
        btn=self.sender()
        if btn.text()=='Show Details':
            
            #! todo
       #     if tab=='edit_configurations':
            self.scrollArea = QtWidgets.QScrollArea()
       #     elif tab=='conf_snapshots':
      #          self.scrollArea = QtWidgets.QScrollArea(self.conf_snapshots)
            self.scrollArea.setWidgetResizable(True)
            self.scrollArea.setObjectName("scrollArea")
            self.scrollAreaWidgetContents = QtWidgets.QWidget()
            self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 295, 108))
            self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
            self.gridLayout_3 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
            self.gridLayout_3.setObjectName("gridLayout_3")
            self.lbl_details = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            
            #! todo here
            
            self.lbl_details.setWordWrap(True)
            self.lbl_details.setObjectName("lbl_details")
            self.lbl_details.setText(self.lbl_details_text)
            self.gridLayout_3.addWidget(self.lbl_details, 0, 0, 1, 1)
            # self.verticalLayout_2.addWidget(self.lbl_details)
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            #if tab=='edit_configurations':
             #   print('yes')
            self.verticalLayout_2.addWidget(self.scrollArea)
            #elif tab=='conf_snapshots':
                # self.VLayout_snapshot.addWidget(self.scrollArea)
                
            btn.setText('Hide Details')
                
        elif btn.text()=='Hide Details':
            
                
            for i in range(self.verticalLayout_2.count()):
                if 'QScrollArea' in str(self.verticalLayout_2.itemAt(i).widget()):
                    self.verticalLayout_2.itemAt(i).widget().deleteLater()
                    break

                
            btn.setText('Show Details')
    
    def btn_set_callback(self):
        grub_timeout_value=self.ledit_grub_timeout.text()
        interrupt=None
        # sleep(5)
        if grub_timeout_value=='0':
            self.ledit_grub_timeout.setText('Use 0.0 instead of 0 ')
            self.ledit_grub_timeout.selectAll()
            self.ledit_grub_timeout.setFocus()
            #! todo here
        else:
            try:
                float(grub_timeout_value)
                
            except Exception as e:
                interrupt=1
                print(e)
                self.ledit_grub_timeout.setText('not a number error')
                self.ledit_grub_timeout.selectAll()
                self.ledit_grub_timeout.setFocus()
        
        #! todo test if this works
        if not (self.verticalLayout_2.itemAt(1) and isinstance(self.verticalLayout_2.itemAt(1),QtWidgets.QHBoxLayout)):
            if self.verticalLayout_2.itemAt(2) is not None:
                print('yes',isinstance(self.verticalLayout_2.itemAt(2).widget(),QtWidgets.QHBoxLayout))
            print(self.verticalLayout_2.itemAt(1))
            #create a label to show user that saving
            self.lbl_status= QtWidgets.QLabel()
            self.lbl_status.setText('saving do not close')
            self.lbl_status.setStyleSheet('color:#03fc6f;')
            
            
            
            # self.verticalLayout.addWidget(self.lbl_status)
            
            # create a button (show details)
            self.btn_show_details= QtWidgets.QPushButton()
            self.btn_show_details.setText('Show Details')
            self.btn_show_details.clicked.connect(partial(self.btn_show_details_callback,'edit_configurations'))
            
            #create a horizontal layout
            self.HLayout_save= QtWidgets.QHBoxLayout()
            self.HLayout_save.addWidget(self.lbl_status)
            self.HLayout_save.addWidget(self.btn_show_details)
            self.verticalLayout_2.addLayout(self.HLayout_save)
            
        else:
            self.lbl_status.setText('saving do not close')
            self.lbl_status.setStyleSheet('color:#03fc6f;')
        
        print(interrupt,'interrupt')
        if not interrupt:
            self.saveConfs()
            

    def btn_show_orginal_callback(self):
        global file_loc
        file_loc='/etc/default/grub'
        self.setUiElements()
        if 'QFrame' in str(self.verticalLayout.itemAt(4).widget()):
            self.verticalLayout.itemAt(4).widget().deleteLater()
        else:
            self.verticalLayout.itemAt(5).widget().deleteLater()
            
            
    def btn_view_callback(self,arg):
        global file_loc
        file_loc= f'{HOME}/.grub_editor/snapshots/'+arg
        self.setUiElements()
        if self.verticalLayout.itemAt(4) is None or not 'QFrame' in str(self.verticalLayout.itemAt(4).widget()):
            #create frame
            self.frame = QtWidgets.QFrame(self.edit_configurations)
            self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
            self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
            self.frame.setObjectName("frame")
            
            
            
            self.lbl_snapshot_view= QtWidgets.QLabel(self.frame)
            self.lbl_snapshot_view.setObjectName('lbl_snapshot_view')
            self.lbl_snapshot_view.setText('You are currently looking at snapshot from '+arg)
            # self.lbl_snapshot_view.setStyleSheet('QLabel{border:1px solid #ff0000;\
            #                                      border-radius: 10px 10px 10px 10px;}')
            self.lbl_snapshot_view.setWordWrap(True)
            self.lbl_snapshot_view.setMinimumSize(100,30)
            self.HLayout_=QtWidgets.QHBoxLayout()
            
            
            # the '.' in the string is there to avoid QLabel getting affected
            self.frame.setStyleSheet('.QFrame{border:1px solid #ff0000;\
                                                 border-radius: 10px 10px 10px 10px;}')
            

            
            
            
            self.HLayout_.setObjectName('HLayout_')
            # self.HLayout_.addWidget(self.lbl_snapshot_view)
            
            #button to reverto to original
            self.btn_show_orginal =QtWidgets.QPushButton(self.frame)
            self.btn_show_orginal.setObjectName('btn_show_original')
            self.btn_show_orginal.setText('Show original configuration')
            self.btn_show_orginal.clicked.connect(self.btn_show_orginal_callback)
            # self.HLayout_.addWidget(self.btn_show_orginal)
            
            
            
            self.gridLayout_3 = QtWidgets.QGridLayout(self.frame)
            self.gridLayout_3.setObjectName("gridLayout_3")
            self.gridLayout_3.addWidget(self.lbl_snapshot_view, 0, 0, 1, 1)
            self.gridLayout_3.addWidget(self.btn_show_orginal, 0, 1, 1, 1)
            self.verticalLayout.addWidget(self.frame)
            
            
            
            # add 20 px margin to top of the HLayout_
            # self.HLayout_.setContentsMargins(0,0,20, 0)
            
            # self.verticalLayout.addLayout(self.HLayout_)
            self.lbl_snapshot_view.setText('You are currently looking at snapshot from '+arg)
            
            
            
            
            
        else:
            self.verticalLayout.itemAt(3)
            self.lbl_snapshot_view.setText('You are currently looking at snapshot from '+arg)
                
    def set_btn_callback(self,line):
        start = perf_counter()
        print(f'pkexec sh -c  \' cp -f  "{HOME}/.grub_editor/snapshots/{line}" {write_file} && sudo update-grub  \' ')
        #! todo here

        
        self.setUiElements()
        end=perf_counter()
        
        if not (self.verticalLayout_2.itemAt(1) and isinstance(self.verticalLayout_2.itemAt(1),QtWidgets.QHBoxLayout)):
            #create a label to show user that saving
            self.lbl_status= QtWidgets.QLabel(self.edit_configurations)
            self.lbl_status.setText('waiting for authentication')
            self.lbl_status.setStyleSheet('color:#03fc6f;')
            
            
            
            # self.verticalLayout.addWidget(self.lbl_status)
            
            # create a button (show details)
            self.btn_show_details= QtWidgets.QPushButton(self.edit_configurations)
            self.btn_show_details.setText('Show Details')
            self.btn_show_details.clicked.connect(partial(self.btn_show_details_callback,'conf_snapshots'))
            
            #create a horizontal layout
            self.HLayout_save= QtWidgets.QHBoxLayout()
            self.HLayout_save.addWidget(self.lbl_status)
            self.HLayout_save.addWidget(self.btn_show_details)
            self.verticalLayout_2.addLayout(self.HLayout_save)
        #print(end-start)
        else:
            self.lbl_status.setText('waiting for authentication')
            
        self.startWorker(line)
    def startWorker(self,line):
        worker = Worker(self.final,line)
        worker.signals.finished.connect(self.setUiElements)
        self.threadpool.start(worker)
        
    def final(self,line):
        try:
            
            #! todo find a way to show an error message if something goes wrong 
            process = subprocess.Popen([f'pkexec sh -c  \' cp -f  "{HOME}/.grub_editor/snapshots/{line}" {write_file}&& sudo update-grub  \' '], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
            self.lbl_details_text='Waiting for authentication \n'
            
            self.set_lbl_details()
            
            self.lbl_status.setText('Waiting for authentication')
            # out = process.communicate()[0].decode()
            # if self.lbl_details is not None:
            #     print('setting')
            #     print(out,'out')
            #     self.lbl_details.setText(out)
            # self.lbl_status.setText('Saved successfully')
            while True:
                print('running')
                authentication_complete=False
                for line in process.stdout:
                    if not authentication_complete:
                        self.lbl_status.setText('Saving configurations')
                        authentication_complete=True
                    sys.stdout.write(line.decode())
                    self.lbl_details_text= self.lbl_details_text+ line.decode()
                    
                    #this handles the case where lbldetails hasnt yet been created
                    if self.lbl_details is not None:
                        
                        #this handles the case where lbl_details_text gets deleted after once its been created
                        try:
                            self.lbl_details.setText(self.lbl_details_text)
                        except:
                            pass
                break

                if self.lbl_details is not None:
                    for line in process.stdout:
                        sys.stdout.write(line.decode())
                        try:
                            last = self.lbl_details.text()
                            print('last is ',last)
                            self.lbl_details.setText(last+line.decode())
                        except:
                            #! todo 
                            print('looks like label was deleted')
                        
                    break
            self.lbl_status.setText('Saved successfully')
        except Exception as e:
            print(e)
            print('error trying to save the configurations')
            self.lbl_status.setText('An error occured when saving')
            self.lbl_status.setStyleSheet('color: red')
    def deleteCallbackCreator(self,arg):
        def func():
            string =f'rm {HOME}/.grub_editor/snapshots/{arg}'
            print(string)
            subprocess.Popen([f'rm \'{HOME}/.grub_editor/snapshots/{arg}\''],shell=True)
            global file_loc
            if file_loc == f'{HOME}/.grub_editor/snapshots/{arg}':
                file_loc='/etc/default/grub'
                if self.verticalLayout.itemAt(3):
                    self.verticalLayout.itemAt(3).widget().deleteLater()
            self.setUiElements()
        return func
    def btn_rename_callback(self,number):
        btn = self.sender()
        if btn.text() == 'rename':
            self.ledit_ = QtWidgets.QLineEdit(self.conf_snapshots)
            self.ledit_.setObjectName(f"ledit_{number}")
            self.ledit_.returnPressed.connect(self.HLayouts_list[number].itemAt(1).widget().click)
            self.rename_line_edits[number]=self.ledit_
            self.targetLabel=self.HLayouts_list[number].itemAt(0).widget()
            
            self.rename_labels[number] = self.targetLabel
            btn.parent().layout().replaceWidget(self.targetLabel,self.ledit_)
            self.targetLabel.deleteLater()
            self.ledit_.setText(self.lines[number])
            self.ledit_.selectAll()
            
            self.ledit_.setFocus()
            btn.setText('set name')
            
        elif btn.text() == 'set name':
            self.targetLabel=self.rename_labels[number]
            self.ledit_ = self.rename_line_edits[number]
            text = self.ledit_.text()
            line=self.lines[number]
            subprocess.Popen([f'mv \'{HOME}/.grub_editor/snapshots/{line}\' \'{HOME}/.grub_editor/snapshots/{text}\' '],shell=True)
            self.lbl_1 =QtWidgets.QLabel(self.conf_snapshots)
            self.lbl_1.setObjectName(f"label{number}")
            self.lbl_1.setText(self.lines[number])
            
            # print(self.targetLabel.parent())
            btn.parent().layout().replaceWidget(self.ledit_,self.lbl_1)
            self.ledit_.deleteLater()
            btn.setText('rename')
            self.setUiElements()
            
        
        
               
    def createSnapshotList(self):
        print('start of errors?')
        contents = subprocess.check_output([f'ls {HOME}/.grub_editor/snapshots/'],shell=True).decode()
        self.lines =contents.splitlines()

        self.HLayouts_list=[]
        number =0
        clearLayout(self.VLayout_snapshot)
        self.btn_create_snapshot = QtWidgets.QPushButton(self.conf_snapshots)
        self.btn_create_snapshot.setObjectName("btn_create_snapshot")
        self.btn_create_snapshot.setText("create a snapshot now")
        self.btn_create_snapshot.clicked.connect(self.createSnapshot)
        self.VLayout_snapshot.addWidget(self.btn_create_snapshot)
        for line in self.lines:
            #first number is 0
            
            self.HLayouts_list.append(QtWidgets.QHBoxLayout())
            self.HLayouts_list[-1].setObjectName(f'HLayout_snapshot{number}')
            
            
            #set all the buttons that appear on conf_snapshots (for a single snapshots)
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
            self.pushButton_2.clicked.connect(partial(self.set_btn_callback,line))
            self.HLayouts_list[-1].addWidget(self.pushButton_2)
            
            self.VLayout_snapshot.addLayout(self.HLayouts_list[-1])
            
            #first number is 0
            
            number +=1

app =QtWidgets.QApplication(sys.argv)
window=Ui()
app.exec_()
