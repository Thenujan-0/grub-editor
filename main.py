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
import json
import random
import math
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtWidgets import QGridLayout, QWidget, QDesktopWidget
import logging
from os_prober import getOs
import chroot

file_loc='/etc/default/grub'

def printer(*args):
    """ writes to log and writes to console """
    time_now = dt.now()
    printer_temp=''
    for arg in args:
        printer_temp= printer_temp +' '+str(arg)
    
    if sys.platform == 'linux':
                                                             #number is in bytes
        if os.stat(f'{HOME}/.grub-editor/logs/main.log').st_size > 5000000:
            
            #only keep last half of the file
            with open(f'{HOME}/.grub-editor/logs/main.log','r') as f:
                data =f.read()
                lendata = len(data)/2
                lendata=math.floor(lendata)
            new_data = data[lendata:]+'\n'
            
            with open(f'{HOME}/.grub-editor/logs/main.log','w') as f:
                f.write(str(time_now)+new_data+'\n')
                
                
        with open(f'{HOME}/.grub-editor/logs/main.log','a') as f:
            f.write(str(time_now)+printer_temp+'\n')
    print(printer_temp)


write_file='/opt/grub_fake.txt'
write_file=file_loc

HOME =os.getenv('HOME')
PATH = os.path.dirname(os.path.realpath(__file__))
to_write_data=None

#create the necessary files and folders
subprocess.Popen([f'mkdir -p {HOME}/.grub-editor/snapshots'],shell=True)
subprocess.Popen([f'mkdir -p {HOME}/.grub-editor/logs'],shell=True)
subprocess.Popen([f'touch {HOME}/.grub-editor/logs/main.log'],shell=True)


#catch the error that occures when this file isnt created yet
try:
    logging.basicConfig(filename=f'{HOME}/.grub-editor/logs/main.log',format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
except:
    subprocess.run([f'mkdir -p {HOME}/.grub-editor/logs'],shell=True)
    subprocess.run([f'touch {HOME}/.grub-editor/logs/main.log'],shell=True)

def check_dual_boot():
    out = subprocess.check_output(['pkexec os-prober'],shell=True).decode()


def getValue(name,issues,read_file=file_loc):
    """arguments are  the string to look for 
    and the list to append issues to"""

    #check if last character is = to avoid possible bugs

    if name[-1] != '=':
        raise Exception("name passed for getvalue doesnt contain = as last character")

    with open(read_file) as file:
        data =file.read()
        start_index =data.find(name)
        end_index =data[start_index+len(name):].find('\n')+start_index+len(name)
        lines=data.splitlines()
        for line in lines:
            if name in line:
                # print(name,'name was found in the line',line)
                if '#' in line :
                    printer('found a line that could possibly commented out',line)
                    string=name+'is commented out in /etc/default/grub'
                    if string not in issues:
                        issues.append(string)
                    return 'None'
        # print(start_index,name)
        if start_index <0:
            string='coudn\'t find '+name+' in /etc/default/grub'
            if string not in issues:
                issues.append(string)
            return "None"
        else:
            if end_index <0:
                return data[start_index+len(name):]
            else:
                return data[start_index+len(name):end_index]





def initialize_temp_file(file_path):
    """copies the file to ~/.cache/grub-editor/temp.txt so that setValue can start writing changes to it"""
    subprocess.run([f'cp {file_path} {HOME}/.cache/grub-editor/temp.txt'],shell=True)


def setValue(name,val):
    """ writes the changes to ~/.cache/grub-editor/temp.txt call initialize_temp_file before start writing to temp.txt"""
    target_file=f'{HOME}/.cache/grub-editor/temp.txt'



    if name[-1] != '=':
        raise Exception("name passed for getvalue doesnt contain = as last character")
    
    with open(target_file,'r') as file:
        printer('file_loc',file_loc)
        to_write_data =file.read()
    start_index =to_write_data.find(name)
    end_index =to_write_data[start_index+len(name):].find('\n')+start_index+len(name)
    
    to_write_data = to_write_data.replace(name+to_write_data[start_index+len(name):end_index],name+str(val))
    lines = to_write_data.splitlines()
    for line in lines:
        if name in line:
            printer('found the name',name,'in the line',line)
            if '#' in line :
                printer('lines seeems to be commented out',line)
                index = lines.index(line)
                new_line =line.replace('#','')
                printer('the commented out lines was replaced with ',new_line)
                lines[index] = new_line
    final_string=''
    for line in lines:
        final_string = final_string+line+'\n'
        
    # printer(final_string)
        
    to_write_data = final_string
    
    subprocess.Popen([f'mkdir -p {HOME}/.cache/grub-editor/'],shell=True)
    subprocess.Popen([f'touch {HOME}/.cache/grub-editor/temp.txt'],shell=True)
    with open(f'{HOME}/.cache/grub-editor/temp.txt','w') as file:
        file.write(to_write_data)
        
        
default_preference="""{
      "view_default": "None",
      "create_snapshot":"None"
}"""

def get_preference(key):
    subprocess.run([f'mkdir -p {HOME}/.grub-editor/preferences/'],shell=True)
    
    if not os.path.exists(f'{HOME}/.grub-editor/preferences/main.json'):
        with open(f'{HOME}/.grub-editor/preferences/main.json','w') as file :
            file.write(default_preference)
        
    file = open(f'{HOME}/.grub-editor/preferences/main.json')
    try:
        dict =json.load(file)
    except Exception as e:
        file.close()
        printer(e)
        printer(traceback.format_exc())
        printer('This exception was handled with ease 😎')
        with open(f'{HOME}/.grub-editor/preferences/main.json','w') as file:
            file.write(default_preference)
            
            
    #reopen the file and then read it
    file = open(f'{HOME}/.grub-editor/preferences/main.json')
    dict =json.load(file)
    file.close()
    value = dict[key]
        
    return value

def set_preference(key,value):
    subprocess.run([f'mkdir -p {HOME}/.grub-editor/preferences/'],shell=True)
    
    if os.path.exists(f'{HOME}/.grub-editor/preferences/main.json'):
        file = open(f'{HOME}/.grub-editor/preferences/main.json')
        dict =json.load(file)
        # printer(dict)
        # printer(type(dict))
        dict[key]=value
        file.close()
    
    pref_file = open(f'{HOME}/.grub-editor/preferences/main.json', "w")
    
    json.dump(dict, pref_file, indent = 6)
    
    pref_file.close()





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


    # this is a decorator
    # now when this run function is executed it actually calls the QtCore.pyqtSlot function wuth run function as argument
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
    resized = QtCore.pyqtSignal()
    # snapshot_lbl_len=18
    snapshot_lbl_len_const=23
    
    
    def resizeEvent(self, event):
        """ resize event handler """
        self.resized.emit()
        return super(Ui, self).resizeEvent(event)
    
    def closeEvent(self,*args,**kwargs):
        super(QtWidgets.QMainWindow, self).__init__()
        
        #todo unmount the mounted devices
        
        
    def someFunction(self):
        # print("someFunction"+str(random.randint(0, 100)))
        # pass
        # width =self.centralWidget().geometry().width()
        # print(width,'width')
        # if width >700:
        # self.snapshot_lbl_len = math.floor((width -700)/20)+self.snapshot_lbl_len_const
            # print (self.snapshot_lbl_len,' snapshot_lbl_len')
        self.createSnapshotList()
            # for layout in self.HLayouts_list:
            #     print(layout.itemAt(0).widget())
            
            
    def __init__(self):
        super(Ui, self).__init__()
        self.threadpool= QtCore.QThreadPool()
        uic.loadUi(f'{PATH}/ui/main1.ui',self)

        #make sure window is in center of the screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        self.show()


        #possible windows that will be created later 

        #a window to show suggestios regarding grub configuration
        self.set_recommendations_window=None
        self.dialog_invalid_default_entry=None

        #handle resize event it is used to define the maximum length of snapshot labels
        self.resized.connect(self.someFunction)


        #dictionary to store qlineEdits for rename .stored widget is qlineEditWidget. key is index of the row
        self.rename_line_edits={}
        
        #dictionary for storing labels (rename) . key is index of the row
        self.btn_set.clicked.connect(self.btn_set_callback)
        self.rename_labels={}
        self.ledit_grub_timeout.setValidator(QtGui.QDoubleValidator())
        self.scrollAreaWidgetContents.adjustSize()
        self.VLayout_snapshot_parent.addStretch()
        
        #load the entries for available operating systems
        import find_entries
        self.main_entries = find_entries.main_entries

        #add all the available operating systems to comboBox_grub_default and self.all_entries
        self.all_entries =[]
        for entry in self.main_entries:
            if len(entry.sub_entries) ==0:
                self.comboBox_grub_default.addItem(entry.title)
                self.all_entries.append(entry.title)
            else:
                for sub in entry.sub_entries:
                    self.comboBox_grub_default.addItem(sub.parent.title+' >'+sub.title)
                    self.all_entries.append(sub.parent.title+' >'+sub.title)
        
        
        #label that shows saving or saved sucessfully
        self.lbl_details=None
        
        #variable to store the execution output  when saving
        self.lbl_details_text=''
        
        self.btn_add.clicked.connect(self.btn_add_callback)
        self.btn_substract.clicked.connect(self.btn_substract_callback)
        self.issues=[]
        
        self.setUiElements()
        
        self.original_modifiers=[]
        self.modified_original =False
        
        
        self.comboBox_configurations.currentIndexChanged.connect(self.load_configuration_from_callback)
        if len(self.issues) > 0:
            self.issuesUi=IssuesUi(self.issues)
            self.issuesUi.show()
        self.ledit_grub_timeout.textChanged.connect(self.ledit_grub_timeout_callback)
        self.predefined.toggled.connect(self.radiobutton_toggle_callback)
        self.comboBox_grub_default.currentIndexChanged.connect(self.comboBox_grub_default_on_current_index_change)
        self.checkBox_boot_default_entry_after.toggled.connect(self.checkBox_boot_default_entry_after_on_toggle)
        self.checkBox_show_menu.toggled.connect(self.checkBox_show_menu_on_toggle)
        self.btn_reset.clicked.connect(self.btn_reset_callback)
        self.tabWidget.currentChanged.connect(self.tabWidget_currentChanged_callback)
        self.checkBox_look_for_other_os.clicked.connect(self.checkBox_look_for_other_os_callback)

        #add chroot to tab


        self.chroot = chroot.ChrootUi()
        self.chroot.setObjectName("chroot")
        self.tabWidget.addTab(self.chroot, "Chroot")
        self.chroot_status='before'
        #update chroot tab
        self.update_chroot_os()

    def update_chroot_os(self):
        """ add the available operating systems to chroot tab """
        operating_systems,partitions=getOs()

        for i,os in enumerate(operating_systems):
            partition =partitions[i]
            item=QtWidgets.QListWidgetItem(os+" on "+partition)
            self.chroot.listWidget.addItem(item)
        self.chroot.listWidget.itemClicked.connect(self.listWidget_itemClicked_callback)

    def btn_exit_chroot_callback(self):
        self.chroot_after.deleteLater()
        self.tabWidget.removeTab(2)
        self.chroot=chroot.ChrootUi()
        self.tabWidget.addTab(self.chroot,'Chroot')
        self.chroot_status='before'
        self.update_chroot_os()
        self.tabWidget.setCurrentIndex(2)

    def listWidget_itemClicked_callback(self, item):
        print(item.text())
        if self.chroot_status == 'before':
            self.chroot.deleteLater()
            self.tabWidget.removeTab(2)

            self.chroot_after=chroot.ChrootAfterUi()
            self.tabWidget.addTab(self.chroot_after,'Chroot')
            self.chroot_status='after'
            
            
            self.tabWidget.setCurrentIndex(2)
            self.chroot_after.btn_exit_chroot.clicked.connect(self.btn_exit_chroot_callback)


        else:
            self.chroot_after.deleteLater()
            self.tabWidget.removeTab(2)
            self.chroot=chroot.ChrootUi()
            self.tabWidget.addTab(self.chroot,'Chroot')
            self.chroot_status='before'

    def tabWidget_currentChanged_callback(self,index):
        # print('index of tab is ',index)
        if index==2:
            def check_os_prober():
                pass
                out = subprocess.check_output(['pkexec os-prober'],shell=True).decode()
                print(out)
            #! todo here use worker to checkthe output and then send a signal once it finishes it


    def ledit_grub_timeout_callback(self):
        value =getValue('GRUB_TIMEOUT=',self.issues)
        text = self.ledit_grub_timeout.text()
        ledit = self.ledit_grub_timeout
        # printer(text,value)
        if text != value:
            if ledit not in self.original_modifiers:
                self.original_modifiers.append(ledit)
        else:
            if ledit in self.original_modifiers:
                self.original_modifiers.remove(ledit)
        self.handle_modify()


    def checkBox_boot_default_entry_after_on_toggle(self):
        """ on toggle handlerfor checkBox_boot_default_entry_after """
        btn =self.sender()
        timeout=getValue('GRUB_TIMEOUT=',self.issues)
        printer(timeout,'timeout')
        if  timeout !='None' and timeout !='-1':
            # printer(timeout)
            if self.checkBox_boot_default_entry_after.isChecked():
                if btn  in self.original_modifiers:
                    self.original_modifiers.remove(btn)
            else:
                if btn not in self.original_modifiers:
                    self.original_modifiers.append(btn)

        elif (timeout == 'None' or timeout =='-1' ) :
            if self.checkBox_boot_default_entry_after.isChecked():
                if btn  not in self.original_modifiers:
                    self.original_modifiers.append(btn)
            else:
                if btn   in self.original_modifiers:
                    self.original_modifiers.remove(btn)

        self.handle_modify()

    def btn_reset_callback(self):
        """ on clicked callback for reset button """

        print('current index of combox configuration is',self.comboBox_configurations.currentIndex())

        self.comboBox_configurations.setCurrentIndex(0)
        self.comboBox_configurations.blockSignals(False)


    def checkBox_show_menu_on_toggle(self):
        """ on toggled handler for checkBox_show_menu """

        timeout_style = getValue('GRUB_TIMEOUT_STYLE=',self.issues)
        btn=self.sender()
        if timeout_style == 'menu':
            if btn.isChecked():
                if btn in self.original_modifiers:
                    self.original_modifiers.remove(btn)
            else:
                if btn not in self.original_modifiers:
                    self.original_modifiers.append(btn)
        elif timeout_style == 'hidden':
            if not btn.isChecked():
                if btn in self.original_modifiers:
                    self.original_modifiers.remove(btn)
            else:
                if btn not in self.original_modifiers:
                    self.original_modifiers.append(btn)
        self.handle_modify()

    def load_configuration_from_callback(self,value):
        global file_loc
        # printer(self.configurations[value],'load configuration from callback')
        value =self.configurations[value]
        if value =='/etc/default/grub':
            file_loc='/etc/default/grub'
        else:
            file_loc=f'{HOME}/.grub-editor/snapshots/{value}'
            
        self.setUiElements()
            
        
        
    def btn_add_callback(self):
        value = self.ledit_grub_timeout.text()
        value =float(value)
        self.ledit_grub_timeout.setText(str(value+1))
        value =getValue('GRUB_TIMEOUT=',self.issues)
        text = self.ledit_grub_timeout.text()
        ledit = self.ledit_grub_timeout
        # printer(text,value)
        if text != value:
            if ledit not in self.original_modifiers:
                self.original_modifiers.append(ledit)
        else:
            if ledit in self.original_modifiers:
                self.original_modifiers.remove(ledit)
        self.handle_modify()
            
        
    def btn_substract_callback(self):
        value =self.ledit_grub_timeout.text()
        value =float(value)
        if value>1:
            
            self.ledit_grub_timeout.setText(str(value-1))
            
        else:
            self.ledit_grub_timeout.setText(str(0.0))
        
        value =getValue('GRUB_TIMEOUT=',self.issues)
        text = self.ledit_grub_timeout.text()
        ledit = self.ledit_grub_timeout
        # printer(text,value)
        if text != value:
            if ledit not in self.original_modifiers:
                self.original_modifiers.append(ledit)
        else:
            if ledit in self.original_modifiers:
                self.original_modifiers.remove(ledit)
        self.handle_modify()

        
    def set_comboBox_grub_default(self):
        """ sets the right index to comboBox_grub_default and radio buttons,
        if second argument is true then value of grub_default by reading will be returned"""
        grub_default_val =getValue('GRUB_DEFAULT=',self.issues)
        if grub_default_val[0]=='"':
            grub_default_val= grub_default_val[1:]
        if grub_default_val[-1]=='"':
            grub_default_val=grub_default_val[:-1]


        print('checking for invalid entry')
        #check if an invalid configuration exists
        if "(INVALID)" in self.all_entries[-1]:
            print("removing invalid entry")
            #todo check if this part is needed in code
            grub_invalid_val = self.all_entries[-1].replace('(INVALID)',"")
            if grub_invalid_val != grub_default_val:
                self.all_entries.pop(-1)
                self.comboBox_grub_default.removeItem(len(self.all_entries))

        else:
            print('no invalid entry found')
            print('last entry is ',self.all_entries[-1])
        
        if grub_default_val=='saved':
            self.previously_booted_entry.setChecked(True)
            # self.comboBox_grub_default.setCurrentIndex(0)
        elif grub_default_val=='None':
            self.previously_booted_entry.setChecked(False)
            self.predefined.setChecked(False)
        else:
            self.predefined.setChecked(True)
            # printer(self.all_entries)
            grub_default_val=grub_default_val.replace('>',' >')
            try:
                self.comboBox_grub_default.setCurrentIndex(self.all_entries.index(grub_default_val))    
            except ValueError:
                self.dialog_invalid_default_entry=DialogUi(btn_cancel=False)
                self.dialog_invalid_default_entry.label.setText("/etc/grub/default currently has an invalid default entry")
                self.dialog_invalid_default_entry.show()

                #add the invalid entry to the combo box
                invalid_value=getValue('GRUB_DEFAULT=',self.issues)
                if invalid_value[0]=='"':
                    invalid_value= invalid_value[1:]
                if invalid_value[-1]=='"':
                    invalid_value=invalid_value[:-1]

                self.comboBox_grub_default.addItem(invalid_value+" (INVALID)")
                self.all_entries.append(invalid_value+"(INVALID)")
                print(self.all_entries[-1],'last item is')
                self.comboBox_grub_default.setCurrentIndex(len(self.all_entries)-1)

    def get_comboBox_grub_default(self):
        """returns the value comboBox grub_default should have"""
        grub_default_val =getValue('GRUB_DEFAULT=',self.issues)
        if grub_default_val[0]=='"':
            grub_default_val= grub_default_val[1:]
        if grub_default_val[-1]=='"':
            grub_default_val=grub_default_val[:-1]
            
        grub_default_val=grub_default_val.replace('>',' >')
        return grub_default_val
                
    def setUiElements(self,reload_confs=True):
        """reloads the ui elements that should be reloaded"""
        
        
        try:
            #catch error that might occur when self.configurations is not initialized
            index =self.comboBox_configurations.currentIndex()
            file_loaded = self.configurations[index]
            # printer('loaded file is',file_loaded)
            if '(modified)' in file_loaded:
                self.configuration_backup=file_loaded
            # todo: do not reload the edit_configurations ui if ui part was modified by user
            # we will think about working on it 🤔
        except AttributeError:
            pass

        finally:

            timeout=getValue('GRUB_TIMEOUT=',self.issues)
            if  timeout !='None' and timeout!='-1':
                # printer(timeout)
                self.ledit_grub_timeout.setText(timeout)
            else:
                self.checkBox_boot_default_entry_after.setChecked(False)



            #stores the available configuration files
            self.configurations=['/etc/default/grub']
            
            #add the available configurations to the combo box
            contents = subprocess.check_output([f'ls {HOME}/.grub-editor/snapshots/'],shell=True).decode()
            self.lines =contents.splitlines()
            # printer(self.lines,'line')
            
            # printer('clearing combo box contents')
            self.comboBox_configurations.blockSignals(True)
            self.comboBox_configurations.clear()
            
            # printer('cleared comboBox contents')
            for line in self.lines:
                self.configurations.append(line)
                # printer(self.configurations)
                
            for item in self.configurations:
                self.comboBox_configurations.addItem(item)
                # printer(self.comboBox_configurations.itemData(123))
            
            global file_loc
            # printer('file_loc is now',file_loc)
            if file_loc=='/etc/default/grub':
                self.comboBox_configurations.setCurrentIndex(0)
            elif '/snapshots/' in file_loc:
                index = file_loc.index('/snapshots/')
                
                snapshot_name= file_loc[index+11:]
                # printer(snapshot_name,'name of the snap shot')
                self.comboBox_configurations.setCurrentIndex(self.configurations.index(snapshot_name))
            
            # printer('added all items to combo box configurations')
            self.comboBox_configurations.blockSignals(False)
            
            
            if getValue('GRUB_TIMEOUT_STYLE=',self.issues)=='hidden':
                self.checkBox_show_menu.setChecked(False)
            elif getValue('GRUB_TIMEOUT_STYLE=',self.issues)=='menu':
                self.checkBox_show_menu.setChecked(True)

            self.set_comboBox_grub_default()
                
            if getValue('GRUB_TIMEOUT=',self.issues)=='-1' or getValue('GRUB_TIMEOUT=',self.issues)=='None':
                self.checkBox_boot_default_entry_after.setChecked(False)
            else:
                self.checkBox_boot_default_entry_after.setChecked(True)
                
            self.createSnapshotList()


            #set the value of checkBox_look_for_other_os
            value = getValue('GRUB_DISABLE_OS_PROBER=',self.issues)
            if value=="false":
                self.checkBox_look_for_other_os.setChecked(True)
            elif value=="true":
                self.checkBox_look_for_other_os.setChecked(False)
            else:
                printer("Unknown value for GRUB_DISABLE_OS_PROBER")
        
        
    def set_lbl_details(self):
        """receives the string in lbl_details_text and sets it as the label for lbl_details"""
        try:
            self.lbl_details.setText(self.lbl_details_text)
        except:
            #this could fail because of two reasons 
            #1.lbl_details hasnt yet been created
            #2.it was deleted
            pass
        
    def saveConfsToCache(self):
        """ saves the configurations that are in GUI to cache ~/.grub-editor/temp.txt  """
        self.lbl_details_text=''
        
        # clear the file in cache
        subprocess.run([f'rm {HOME}/.cache/grub-editor/temp.txt'],shell=True)
        subprocess.run([f'mkdir -p {HOME}/.cache/grub-editor'],shell=True)
        subprocess.run([f'touch {HOME}/.cache/grub-editor/temp.txt'],shell=True)

        index =self.comboBox_configurations.currentIndex()
        total=len(self.configurations)
        if index ==0 or (index==total-1 and "(modified)" in self.configurations[-1]):
            target_file_copy = '/etc/default/grub'
        else:
            target_file_copy =f'{HOME}/.grub-editor/snapshots/'+self.configurations[index]

        initialize_temp_file(target_file_copy)
        
        if self.checkBox_show_menu.isChecked():
            setValue('GRUB_TIMEOUT_STYLE=','menu')
        else:
            setValue('GRUB_TIMEOUT_STYLE=','hidden')
        
        # printer('save condfs to cache was called')
        if self.predefined.isChecked():
            # printer('predefined is checked')
            self.grub_default =str(self.comboBox_grub_default.currentText())

            if self.grub_default.count('>') <=1:

                if '>' in self.grub_default:
                    front_part=self.grub_default[:self.grub_default.find(' >')]
                    last_part=self.grub_default[self.grub_default.find('>'):]
                    to_write='"'+front_part+last_part+'"'
                    setValue('GRUB_DEFAULT=',to_write)
                    # printer('called:''GRUB_DEFAULT=',to_write)
                    # printer(to_write+'part to be written')
                else:
                    setValue('GRUB_DEFAULT=','\"'+self.grub_default+'\"')
                    # printer('called:''GRUB_DEFAULT='+'\"'+self.grub_default+'\"')
                    # printer('woke from 20 sec sleep')
                #set the value of grub_default
            else:
                printer('Error occured when setting grub default as combobox text has more than one  1\' >\'  ')
                self.lbl_status.setText('Error occured when setting grub default as combobox text has more than one  1\' >\'  ')
                printer(self.grub_default)
        elif self.previously_booted_entry.isChecked():
            # printer('i\'m not Supposed to be printed')
            setValue('GRUB_DEFAULT=','saved')

        if self.checkBox_boot_default_entry_after.isChecked():
            setValue('GRUB_TIMEOUT=',self.ledit_grub_timeout.text())
            # printer('setting grub-timeout')

        else:
            setValue('GRUB_TIMEOUT=','-1')
            # printer('setting grub-timeout -1')

        #look for other os
        if self.checkBox_look_for_other_os.isChecked():
            setValue("GRUB_DISABLE_OS_PROBER=","false")
        else:
            setValue("GRUB_DISABLE_OS_PROBER","true")

    def saveConfs(self):
        """ copies the configuration file from cache to the target(/etc/default/grub) """
        self.saveConfsToCache()

        def final(self):
            try:
                
                process = subprocess.Popen([f' pkexec sh -c \'echo \"authentication completed\"  && \
                        cp -f  "{HOME}/.cache/grub-editor/temp.txt"  '+write_file +' && sudo update-grub 2>&1 \'  '],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True)
                self.lbl_details_text='Waiting for authentication \n'
                
                self.set_lbl_details()
                
                self.lbl_status.setText('Waiting for authentication')
                # out = process.communicate()[0].decode()
                # if self.lbl_details is not None:
                #     printer('setting')
                #     printer(out,'out')
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

                    # if self.lbl_details is not None:
                    #     for line in process.stdout:
                    #         sys.stdout.write(line.decode())
                    #         try:
                    #             last = self.lbl_details.text()
                    #             printer('last is ',last)
                    #             self.lbl_details.setText(last+line.decode())
                    #         except:
                    #             printer('looks like label was deleted')
                            
                    #     break
                if not authentication_error:
                    self.lbl_status.setText('Saved successfully')
                else:
                    self.lbl_status.setText('Authentication error occured')
                    self.lbl_status.setStyleSheet('color: red')
                        
            except Exception as e:
                printer(e)
                printer('error trying to save the configurations')
                printer(traceback.format_exc())
                self.lbl_status.setText('An error occured when saving')
                self.lbl_status.setStyleSheet('color: red')
        # threading.Thread(target=final,args=[self]).start()
        self.startWorker(final,self.setUiElements,None,self)

    def checkBox_look_for_other_os_callback(self):
        """ callback handler for checkBox_look_for_other_os
            reacts to modifications
        """
        value=getValue("GRUB_DISABLE_OS_PROBER=",self.issues)
        cbox=self.checkBox_look_for_other_os

        #check if cbox is showing right value
        if (value=="true" and not cbox.isChecked() or value=="false" and cbox.isChecked()) \
            and cbox in self.original_modifiers:
            
            
                self.original_modifiers.remove(cbox)
        # check if cbox is showing false value 
        elif ( (value=="true" and  cbox.isChecked()) or (value=="false" and not cbox.isChecked()) ) \
            and cbox not in self.original_modifiers:
            self.original_modifiers.append(cbox)
        else:
            printer("unknown case in checkbox_look_for_other_os_callback"+"\n"+
                            "value of checkBox.isChecked is "+str(cbox.isChecked())+"\n"+
                            "value of GRUB_DISABLE_OS_PROBER= is "+str(value))

        self.handle_modify()
        
        
    def btn_create_snapshot_callback(self):
        preference= get_preference("create_snapshot")
        # printer(preference)
        if preference=="None" and len(self.original_modifiers)>0:
            self.create_snapshot_dialog = CreateSnapshotUi()
            self.create_snapshot_dialog.btn_ignore_changes.clicked.connect(self.btn_ignore_changes_callback)
            self.create_snapshot_dialog.btn_add_changes_to_snapshot.clicked.connect(self.btn_add_changes_to_snapshot_callback)
            self.create_snapshot_dialog.show() 
        elif preference=='add_changes_to_snapshot':
            self.saveConfsToCache()
            # printer('saving from cache')
            self.createSnapshot(from_cache=True)
        elif preference=='ignore_changes' or preference =='None':
            #preference is == None here means that nothing was modified in UI and preference file is fresh
            self.createSnapshot()

        else:
            printer('WARNING: preference unhandled case')
            printer("preference value is :",preference)




    def btn_add_changes_to_snapshot_callback(self):
        """part of CreateSnapshotUi window"""
        checked=self.create_snapshot_dialog.checkBox_do_this_everytime.isChecked()
        if checked:
            set_preference("create_snapshot","add_changes_to_snapshot")
        self.saveConfsToCache()
        self.createSnapshot(from_cache=True)
        self.create_snapshot_dialog.close()

    def btn_ignore_changes_callback(self):
        """ a part of CreateSnapshotUi window """
        self.createSnapshot()
        self.create_snapshot_dialog.close()
        checked=self.create_snapshot_dialog.checkBox_do_this_everytime.isChecked()
        if checked:
            set_preference("create_snapshot","ignore_changes")


    def createSnapshot(self,from_cache=False):
        """ creates a snapshot of /etc/default/grub and saves to ~/grub-editor/{date_time}
        if from_cache is true then copies the file in cache(~/.cache/grub-editor/temp.txt) to ~/grub-editor/{date_time}  """
        with open(file_loc) as file:
            data= file.read()
        date_time =str(dt.now()).replace(' ','_')[:-7]
        if not from_cache:
            subprocess.Popen([f'touch {HOME}/.grub-editor/snapshots/{date_time}'],shell=True)
            with open(f'{HOME}/.grub-editor/snapshots/{date_time}','w') as file:
                file.write(data)
        else:
            # printer('created a snapshot grom cache')
            subprocess.run([f'cp {HOME}/.cache/grub-editor/temp.txt {HOME}/.grub-editor/snapshots/{date_time}'],shell=True)
        self.setUiElements()

        #todo : fix that changes made in ui get lost when creating a snapshot


    def btn_show_details_callback(self,tab):
        # printer(self.verticalLayout_2.itemAt(1))
        target_index=None
        for i in range(self.verticalLayout_2.count()):
            if isinstance(self.verticalLayout_2.itemAt(i),QtWidgets.QHBoxLayout):
                # printer(self.verticalLayout_2.itemAt(i).itemAt(0).widget())
                target = self.findChild(QtWidgets.QHBoxLayout,'HLayout_save')
                # printer(target,'target')
                # printer('yes')
                if target==self.verticalLayout_2.itemAt(i):
                    # printer('found target',i)
                    target_index=i
                    break
            # printer(i)
        btn=self.sender()
        if btn.text()=='Show Details':
            
            self.scrollArea = QtWidgets.QScrollArea()
            self.scrollArea.setWidgetResizable(True)
            self.scrollArea.setObjectName("scrollArea")
            self.scrollAreaWidgetContents = QtWidgets.QWidget()
            self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 295, 108))
            self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
            self.gridLayout_3 = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
            self.gridLayout_3.setObjectName("gridLayout_3")
            self.lbl_details = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            
            
            self.lbl_details.setWordWrap(True)
            self.lbl_details.setObjectName("lbl_details")
            self.lbl_details.setText(self.lbl_details_text)
            self.gridLayout_3.addWidget(self.lbl_details, 0, 0, 1, 1)
            # self.verticalLayout_2.addWidget(self.lbl_details)
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            #if tab=='edit_configurations':
             #   printer('yes')
            self.verticalLayout_2.insertWidget(target_index+1,self.scrollArea)
            #elif tab=='conf_snapshots':
                # self.VLayout_snapshot.addWidget(self.scrollArea)
                
            btn.setText('Hide Details')
                
        elif btn.text()=='Hide Details':
            
                
            for i in range(self.verticalLayout_2.count()):
                if 'QScrollArea' in str(self.verticalLayout_2.itemAt(i).widget()):
                    self.verticalLayout_2.itemAt(i).widget().deleteLater()
                    break

                
            btn.setText('Show Details')
    
    def btn_set_callback(self,unsafe=False):

        """ if argument is true then it checks configurations for recommendations and errors """

        #todo check if the interrupt variable usage in here actually does what i expect

        self.recommendations=[]
        self.recmds_fixes=[]
        grub_timeout_value=self.ledit_grub_timeout.text()
        interrupt=0
        # sleep(5)
        # if safe:
        if self.checkBox_boot_default_entry_after.isChecked() and grub_timeout_value=='0':
            # self.ledit_grub_timeout.setText('Use 0.0 instead of 0 ')
            # self.ledit_grub_timeout.selectAll()
            # self.ledit_grub_timeout.setFocus()
            self.recommendations.append('If you are doing dual boot it is preffered to use 0.0 instead of 0 as timeout')
            def temp():
                self.ledit_grub_timeout.setText('0.0')
            self.recmds_fixes.append(temp)


        elif self.checkBox_boot_default_entry_after.isChecked() :
            try:
                float(grub_timeout_value)
                #? kinda dead code here
            except Exception as e:
                interrupt+=1
                printer(e)
                # self.lbl_status.setText('not a number error')
                # self.set_errors.append('')
                self.ledit_grub_timeout.selectAll()
                self.ledit_grub_timeout.setFocus()
        
        
        if not (self.verticalLayout_2.itemAt(1) and isinstance(self.verticalLayout_2.itemAt(1),QtWidgets.QHBoxLayout)):
            if self.verticalLayout_2.itemAt(2) is not None:
                # printer('yes',isinstance(self.verticalLayout_2.itemAt(2).widget(),QtWidgets.QHBoxLayout))
                pass
            # printer(self.verticalLayout_2.itemAt(1))
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
            self.HLayout_save.setObjectName('HLayout_save')
            self.HLayout_save.addWidget(self.lbl_status)
            self.HLayout_save.addWidget(self.btn_show_details)
            self.verticalLayout_2.addLayout(self.HLayout_save)
            
            
            
        else:
            self.lbl_status.setText('saving do not close')
            self.lbl_status.setStyleSheet('color:#03fc6f;')
        
        
        # printer(interrupt,'interrupt')
        if not unsafe:
            if not interrupt and len(self.recommendations)==0:
                self.saveConfs()
            if len(self.recommendations)>0:
                self.set_recommendations_window=SetRecommendations(self.recommendations,self.recmds_fixes)
                self.set_recommendations_window.show()
        else:
            self.saveConfs()

            

    def btn_show_orginal_callback(self):
        global file_loc
        file_loc='/etc/default/grub'
        self.sender().parent().deleteLater()
        self.setUiElements()

            
            
    def btn_view_callback(self,arg):
        try:
            global file_loc
            file_loc= f'{HOME}/.grub-editor/snapshots/'+arg
            self.setUiElements()
            view_default=get_preference('view_default')
            self.view_btn_win =ViewButtonUi(file_loc)
            if view_default=='None':
                
                self.view_btn_win.show()
            elif view_default=='on_the_application_itself':
                
                self.view_btn_win.btn_on_the_application_itself_callback()
                
            elif view_default=='default_text_editor':
                self.view_btn_win.btn_default_text_editor_callback()
            else:
                printer('ERROR: unknown value for view_default on main.json',view_default)
        except Exception as e:
            printer(str(e))
            printer(traceback.format_exc())
            printer("An error occured in btn_View_callback")
                
    def btn_set_snapshot(self,line):
        """ callback back function for set snapshot button """

        try:

            # all the code that has to be executed to set the snapshot are inside this function
            def set_snapshot():
                
                if not (self.verticalLayout_2.itemAt(1) and isinstance(self.verticalLayout_2.itemAt(1),QtWidgets.QHBoxLayout)) and \
                    not (self.verticalLayout_2.itemAt(2) and isinstance(self.verticalLayout_2.itemAt(2),QtWidgets.QHBoxLayout)):
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
                    self.HLayout_save.setObjectName('HLayout_save')
                    self.HLayout_save.addWidget(self.lbl_status)
                    self.HLayout_save.addWidget(self.btn_show_details)
                    self.verticalLayout_2.addLayout(self.HLayout_save)
                #printer(end-start)
                else:
                    self.lbl_status.setText('waiting for authentication')
                    
                self.startWorker(self.final,self.setUiElements,None,line)
                if self.dialog_invalid_default_entry :
                    self.dialog_invalid_default_entry.close()


            #check if snapshot's default os is a valid one 
            default=getValue("GRUB_DEFAULT=",self.issues,f"{HOME}/.grub-editor/snapshots/{line}")

            if default not in self.all_entries:
                printer("Value of default in snapshot is not a valid os")
                self.dialog_invalid_snapshot=DialogUi(btn_cancel=True)
                self.dialog_invalid_snapshot.label.setText("The snapshot you have selected has an invalid value for grub default")
                self.dialog_invalid_snapshot.btn_ok.setText('continue anyway')
                self.dialog_invalid_snapshot.show()
                self.dialog_invalid_snapshot.btn_ok.clicked.connect(set_snapshot)



            # printer(f'pkexec sh -c  \' cp -f  "{HOME}/.grub-editor/snapshots/{line}" {write_file} && sudo update-grub  \' ')

            
        except Exception as e:
            printer(traceback.format_exc())
            printer(str(e))
            printer('Error occured in btn_set_snapshot')


    def startWorker(self,toCall,onFinish,onResult,*args):
        try:
            """ arguments are funtion to run , funtion to call when finishes ,function to call with result if no errors occured, arugments of the first funtion """
            worker = Worker(toCall,*args)
            if onFinish is not None:
                worker.signals.finished.connect(onFinish)
            if onResult is not None:
                worker.signals.result.connect(onResult)
            self.threadpool.start(worker)
        except Exception as e:
            printer(traceback.format_exc())
            printer(str(e))
        
    def final(self,line):
        try:
            # print('executing the command')
            # print(f'pkexec sh -c  \' cp -f  "{HOME}/.grub-editor/snapshots/{line}" {write_file} && sudo update-grub  \' ')
            process = subprocess.Popen([f'pkexec sh -c  \' cp -f  "{HOME}/.grub-editor/snapshots/{line}" {write_file} && sudo update-grub  \' '], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
            self.lbl_details_text='Waiting for authentication \n'
            
            self.set_lbl_details()
            
            self.lbl_status.setText('Waiting for authentication')
            # out = process.communicate()[0].decode()
            # if self.lbl_details is not None:
            #     printer('setting')
            #     printer(out,'out')
            #     self.lbl_details.setText(out)
            # self.lbl_status.setText('Saved successfully')
            while True:
                # printer('running')
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
                            printer('last is ',last)
                            self.lbl_details.setText(last+line.decode())
                        except:
                            printer('looks like label was deleted')
                        
                    break
            if 'done' in self.lbl_details_text:
                self.lbl_status.setText('Saved successfully')
            else:
                self.lbl_status.setText('Saving Failed')
                self.lbl_status.setStyleSheet('color:red')
        except Exception as e:
            printer(e)
            printer('error trying to save the configurations')
            self.lbl_status.setText('An error occured when saving')
            self.lbl_status.setStyleSheet('color: red')
            
            
            
    def deleteCallbackCreator(self,arg):
        def func():
            string =f'rm {HOME}/.grub-editor/snapshots/{arg}'
            printer(string)
            subprocess.Popen([f'rm \'{HOME}/.grub-editor/snapshots/{arg}\''],shell=True)
            global file_loc
            if file_loc == f'{HOME}/.grub-editor/snapshots/{arg}':
                file_loc='/etc/default/grub'
                if self.verticalLayout.itemAt(3):
                    self.verticalLayout.itemAt(3).widget().deleteLater()
            self.setUiElements()
        return func
    def btn_rename_callback(self,number):
        try:
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
                subprocess.Popen([f'mv \'{HOME}/.grub-editor/snapshots/{line}\' \'{HOME}/.grub-editor/snapshots/{text}\' '],shell=True)
                self.lbl_1 =QtWidgets.QLabel(self.conf_snapshots)
                self.lbl_1.setObjectName(f"label{number}")
                self.lbl_1.setText(self.lines[number])
                
                # printer(self.targetLabel.parent())
                btn.parent().layout().replaceWidget(self.ledit_,self.lbl_1)
                self.ledit_.deleteLater()
                btn.setText('rename')
                self.setUiElements()
        except Exception as e:
            printer(traceback.format_exc())
            printer(str(e))
        
        
        
    def reconnect(self,signal ,new_handler=None,old_handler=None):
        try:
            if old_handler is not None:
                while True:
                    signal.disconnect(old_handler)
            else:
                signal.disconnect()
        except TypeError:
            pass
        if new_handler is not None:
            # printer(signal)
            signal.connect(new_handler)
            
    def insertInto(self,layout,index,widget):
        items=[]
        for i in reversed(range(layout.count(),index)):
            item =self.itemAt(i).widget()
            item.setParent(None)
            items.append(item)
            # printer(item,'item')
            
        # printer('widget',widget)
            
        layout.addWidget(widget)
        for i in reversed(range(len(items))):
            layout.addWidget(items[i])

    def comboBox_grub_default_on_current_index_change(self):
        try:
            """ current index changed callback """
            # printer('combo box currentIndexChanged')
            comboBox = self.sender()
            combo_text =self.all_entries[comboBox.currentIndex()]
            grub_default = self.get_comboBox_grub_default()
            if grub_default !=combo_text and not self.modified_original:
                # self.modified_original = True
                if comboBox not in self.original_modifiers:
                    self.original_modifiers.append(self.sender())
                # printer(grub_default,combo_text)
            elif grub_default ==combo_text:
                if comboBox in self.original_modifiers:
                    self.original_modifiers.remove(comboBox)

            # printer('modifed original is now',self.modified_original)
            # printer('original modifiers',self.original_modifiers)
            # printer(self.comboBox_configurations.itemData(1))
            self.handle_modify()
        except Exception as e:
            printer(traceback.format_exc())
            printer(str(e))


    def get_radiobutton_predefined(self):
        """returns the value radio button predefined should have now"""
        
        
    def radiobutton_toggle_callback(self):
        try:
            btn= self.sender()
            grub_default_val =self.get_comboBox_grub_default()

                
            
            # printer(btn.text(),'btn.text() radiobutton_toggle_callback')
            if btn.text()=='predefined:':
                # printer('yes')
                default_entry =getValue('GRUB_DEFAULT=',self.issues)
                # printer('grub_default')
                if (default_entry !='saved' and default_entry.lower() !='none') and btn.isChecked():
                    if btn  in self.original_modifiers:
                        self.original_modifiers.remove(btn)  
                    # printer('1st')  
                elif (default_entry =='saved' or default_entry.lower() =='none') and not btn.isChecked():
                    if btn in self.original_modifiers:
                        self.original_modifiers.remove(btn)
                    # printer('2nd')
                else:
                    # printer('last')
                    if btn not in self.original_modifiers:
                        self.original_modifiers.append(btn)
            # printer(self.original_modifiers)
            self.handle_modify()

        except Exception as e:
            printer(traceback.format_exc())
            printer(str(e))

    def handle_modify(self):
        
        """ handles when the loaded configuration is modified in the apps . 
        it changes the loaded configuration from combo box value""" 
        # print('handle_modify: start',self.original_modifiers)
        try:
            if len(self.original_modifiers)>0:
                current_item = self.configurations[self.comboBox_configurations.currentIndex()]
                # printer(current_item)
                if '(modified)' not in current_item:
                    stringy=current_item+'(modified)'
                    self.comboBox_configurations.blockSignals(True)
                    self.comboBox_configurations.addItem(stringy)
                    self.configurations.append(stringy)
                    self.comboBox_configurations.setCurrentIndex(self.comboBox_configurations.count()-1)
                    self.comboBox_configurations.blockSignals(False)
            else:
                index_to_remove =[]
                self.comboBox_configurations.blockSignals(True)
                for item in self.configurations:
                    
                    if '(modified)' in item:
                        item_name = item.replace('(modified)','')
                        index_to_put_after = self.configurations.index(item_name)
                        # printer(item_name)
                        index_to_remove.append(self.configurations.index(item))
                        self.comboBox_configurations.removeItem(self.configurations.index(item))
                        self.comboBox_configurations.setCurrentIndex(index_to_put_after)
                        break
                self.comboBox_configurations.blockSignals(False)
                # printer(index_to_remove)
        except Exception as e:
            printer(traceback.format_exc())
            printer(str(e))
        
        # print('handle_modify: end',self.original_modifiers)
        
    def createSnapshotList(self):
        try:
            contents = subprocess.check_output([f'ls {HOME}/.grub-editor/snapshots/'],shell=True).decode()
            self.lines =contents.splitlines()

            self.HLayouts_list=[]
            number =0
            clearLayout(self.VLayout_snapshot)

            self.reconnect(self.btn_create_snapshot.clicked,self.btn_create_snapshot_callback)
            # self.VLayout_snapshot.addWidget(self.btn_create_snapshot)
            # printer(len(self.lines))
            if len(self.lines) >0 and  self.lbl_no_snapshots:
                self.lbl_no_snapshots.setText('Snapshots are backups of /etc/default/grub .Snapshots can help you when you mess up some configuration in /etc/default/grub . These snapshots are stored inside ~/.grub-editor/snapshots/')
                # self.lbl_no_snapshots= None
                
            elif len(self.lines) ==0 :
                printer('lines are zero and label wasnt found soo.. creating that lbl_nosnapshots')
                # self.lbl_no_snapshots = QtWidgets.QLabel(self.conf_snapshots)
                # self.lbl_no_snapshots.setWordWrap(True)
                # self.lbl_no_snapshots.setObjectName("lbl_no_snapshots")
                self.lbl_no_snapshots.setText('Looks like you dont have any snapshots .Snapshots are backups of /etc/default/grub .Snapshots can help you when you mess up some configuration in /etc/default/grub . These snapshots are stored inside ~/.grub-editor/snapshots/')
                self.lbl_no_snapshots.setWordWrap(True)
                # self.gridLayout_2.addWidget(self.lbl_no_snapshots, 1, 0, 1, 1)
                # self.insertInto(self.gridLayout_2,1,self.lbl_no_snapshots)
                # printer(self.gridLayout_2.itemAt(1))
            else:
                printer('unexpected condition in line 895 when loking for lbl_no_snapshots')
            for line in self.lines:
                #first number is 0
                
                self.HLayouts_list.append(QtWidgets.QHBoxLayout())
                self.HLayouts_list[-1].setObjectName(f'HLayout_snapshot{number}')
                
                
                #set all the buttons that appear on conf_snapshots (for a single snapshots)
                self.lineEdit = QtWidgets.QLabel(self.conf_snapshots)
                self.lineEdit.setObjectName(f"lbl_snapshot{number}")
                width =self.centralWidget().geometry().width()

                
                self.snapshot_lbl_len = math.floor((width -700)/50)+self.snapshot_lbl_len_const
                    # printer (self.snapshot_lbl_len,' snapshot_lbl_len')
                    # self.createSnapshotList()
                    # for layout in self.HLayouts_list:
                        # printer(layout.itemAt(0).widget())
                if len(line) <self.snapshot_lbl_len:
                    self.lineEdit.setText(line)
                else:
                    self.lineEdit.setText(line[:self.snapshot_lbl_len-3]+'...')
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
                self.pushButton_2.clicked.connect(partial(self.btn_set_snapshot,line))
                self.HLayouts_list[-1].addWidget(self.pushButton_2)
                
                self.VLayout_snapshot.addLayout(self.HLayouts_list[-1])
                
                #first number is 0
                
                number +=1
        except Exception as e:
            printer(traceback.format_exc())
            printer(str(e))
            
            
            
class IssuesUi(QtWidgets.QMainWindow):
    def __init__(self,issues):
        super(IssuesUi, self).__init__()
        uic.loadUi(f'{PATH}/ui/issues.ui',self)
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        for issue in issues:
            printer(issue)
            self.listWidget.addItem(issue)
        
class ViewButtonUi(QtWidgets.QDialog):
    def __init__(self,file_location):
        self.file_location = file_location
        super(ViewButtonUi, self).__init__()
        uic.loadUi(f'{PATH}/ui/view_snapshot.ui',self)
        self.btn_on_the_application_itself.clicked.connect(self.btn_on_the_application_itself_callback)
        self.btn_default_text_editor.clicked.connect(self.btn_default_text_editor_callback)

        #create window in the center of the screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def safe_close(self,arg):
        """makes sure the properties of checkbox is saved"""
        if self.checkBox_do_this_everytime.isChecked():
            set_preference('view_default',arg)
        self.close()
        
    def btn_default_text_editor_callback(self):
        self.safe_close('default_text_editor')
        subprocess.Popen([f'xdg-open \'{self.file_location}\''],shell=True)
        
    def btn_on_the_application_itself_callback(self):
        window.tabWidget.setCurrentIndex(0)
        self.safe_close('on_the_application_itself')
        
class CreateSnapshotUi(QtWidgets.QMainWindow):
    def __init__(self):
        super(CreateSnapshotUi, self).__init__()
        uic.loadUi(f'{PATH}/ui/create_snapshot_dialog.ui',self)
        
        #Put the window in the center of the screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())


class SetRecommendations(QtWidgets.QMainWindow):
    def __init__(self,recommendations_list,fixes_list):
        super(SetRecommendations,self).__init__()
        uic.loadUi(f'{PATH}/ui/set_recommendations.ui',self)

        #Put the window in the center of the screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.fixes_list =fixes_list
        
        for i in range(len(recommendations_list)):
            recommendation =recommendations_list[i]
            self.horizontalLayout = QtWidgets.QHBoxLayout()
            self.horizontalLayout.setObjectName("horizontalLayout")
            self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            self.label.setWordWrap(True)
            self.label.setObjectName("label")
            self.label.setText(recommendation)
            self.horizontalLayout.addWidget(self.label)
            spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            self.horizontalLayout.addItem(spacerItem)
            self.pushButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
            self.pushButton.setObjectName("pushButton")
            self.pushButton.setText('Fix')
            # print(self.horizontalLayout)


            self.pushButton.clicked.connect(self.btn_fix_callback_creator(self.horizontalLayout,fixes_list[i],self.verticalLayout_2))
            self.horizontalLayout.addWidget(self.pushButton)
            self.pushButton_2 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
            self.pushButton_2.setObjectName("pushButton_2")
            self.pushButton_2.setText("Ignore")
            self.horizontalLayout.addWidget(self.pushButton_2)
            # self.HLayouts.append(self.horizontalLayout)
            self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.btn_ignore_all.clicked.connect(self.btn_ignore_all_callback)
        self.btn_fix_all.clicked.connect(self.btn_fix_all_callback)

    def btn_ignore_all_callback(self):
        window.btn_set_callback(unsafe=True)
        window.set_recommendations_window.close()

    def btn_fix_all_callback(self):
        for fix in self.fixes_list:
            fix()
        window.btn_set_callback()
        window.set_recommendations_window.close()


    def btn_fix_callback_creator(self,HLayout,fix,verticalLayout_2):
        """ first argument is the HorizontalLayout of button and second argument is the function that fixes the issue
        and the third the the vertical layout where these horizontal layout are located"""
        def btn_fix_callback(self):
            fix()
            clearLayout(HLayout)

            if verticalLayout_2.count() == 0:
                window.set_recommendations_window.close()
                window.btn_set_callback()       
     

        return btn_fix_callback

    def btn_ignore_callback_creator(self,HLayout):
        def btn_ignore_callback(self):
            clearLayout(HLayout)
        return btn_ignore_callback



class DialogUi(QtWidgets.QDialog):
    def __init__(self,btn_cancel=True):
        super(DialogUi,self).__init__()
        # print(PATH)
        uic.loadUi(f'{PATH}/ui/dialog.ui',self)
        if not btn_cancel:
            self.horizontalLayout.takeAt(0).widget().deleteLater()
        else:
            self.btn_cancel.clicked.connect(self.btn_cancel_callback)
        self.btn_ok.clicked.connect(self.btn_ok_callback)

        
        #make sure window is in center of the screen
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def btn_ok_callback(self):
        self.close()

    def btn_cancel_callback(self):
        self.close()


app =QtWidgets.QApplication(sys.argv)
window=Ui()
app.exec_()