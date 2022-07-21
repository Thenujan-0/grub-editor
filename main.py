#!/usr/bin/python
from pickle import TRUE
from venv import create


import sys
from functools import partial
import re
import subprocess
import threading
from datetime import datetime as dt
from time import sleep
from time import perf_counter

import os
from subprocess import PIPE, Popen
import traceback
import json
import random
import math 
import logging
from threading import Thread

from PyQt5 import QtCore ,QtWidgets, uic,QtGui
from PyQt5.QtWidgets import QDesktopWidget



from libs.qt_functools import insert_into, reconnect
from libs.worker import Worker
from libs.find_entries import GrubConfigNotFound, find_entries

from widgets.dialog import DialogUi
from widgets.error_dialog import ErrorDialogUi
from widgets.loading_bar import LoadingBar

GRUB_CONF_LOC='/etc/default/grub'
file_loc=GRUB_CONF_LOC
HOME =os.getenv('HOME')
DEBUG=True
if os.getenv("XDG_CONFIG_HOME") is None:
    CONFIG_LOC=HOME+"/.config/grub-editor"
else:
    CONFIG_LOC=os.getenv("XDG_CONFIG_HOME")+"/grub-editor"
    
if os.getenv("XDG_CACHE_HOME") is None:
    CACHE_LOC=HOME+"/.cache/grub-editor"
else:
    CACHE_LOC=os.getenv("XDG_CACHE_HOME")+"/grub-editor"
    
if os.getenv("XDG_DATA_HOME") is None:
    DATA_LOC=HOME+"/.local/share/grub-editor"
else:
    DATA_LOC=os.getenv("XDG_DATA_HOME")+"/grub-editor"
    
    

def printer(*args):
    """ writes to log and writes to console """
    time_now = dt.now()
    printer_temp=''
    for arg in args:
        printer_temp= printer_temp +' '+str(arg)
    
    if sys.platform == 'linux':

        if os.stat(f'{DATA_LOC}/logs/main.log').st_size > 5000000:#number is in bytes
            
            #only keep last half of the file
            with open(f'{DATA_LOC}/logs/main.log','r') as f:
                data =f.read()
                lendata = len(data)/2
                lendata=math.floor(lendata)
            new_data = data[lendata:]+'\n'
            
            with open(f'{DATA_LOC}/logs/main.log','w') as f:
                f.write(str(time_now)+new_data+'\n')
                
                
        with open(f'{DATA_LOC}/logs/main.log','a') as f:
            f.write(str(time_now)+printer_temp+'\n')
    print(printer_temp)


write_file='/opt/grub_fake.txt'
write_file=file_loc

PATH = os.path.dirname(os.path.realpath(__file__))

#create the necessary files and folders
subprocess.Popen([f'mkdir -p {DATA_LOC}/snapshots'],shell=True)
subprocess.Popen([f'mkdir -p {DATA_LOC}/logs'],shell=True)
subprocess.Popen([f'touch {DATA_LOC}/logs/main.log'],shell=True)


#catch the error that occures when this file isnt created yet
try:
    logging.basicConfig(filename=f'{DATA_LOC}/logs/main.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
except FileNotFoundError:
    
    subprocess.run([f'mkdir -p {DATA_LOC}/logs'],shell=True)
    subprocess.run([f'touch {DATA_LOC}/logs/main.log'],shell=True)
    logging.basicConfig(filename=f'{DATA_LOC}/logs/main.log',
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    

# def check_dual_boot():
#    out = subprocess.check_output(['pkexec os-prober'],shell=True).decode()

def remove_quotes(value:str)->str:
    """ Removes double quotes or single quotes from the begining and the end
        Only if the exist in both places
    """
    if value[0]=='"' and value[-1]=='"':
        value=value[1:-1]
    elif value[0]=="'" and value[-1]=="'":
        value=value[1:-1]
    
    return value

available_conf_keys=["GRUB_DEFAULT=","GRUB_DISABLE_OS_PROBER=",
                    "GRUB_TIMEOUT_STYLE=","GRUB_TIMEOUT=","GRUB_CMDLINE_LINUX="]

def get_value(name,issues,read_file=None):
    """arguments are  the string to look for 
    and the list to append issues to
    Note: It does some minor edits to the value read from the file before 
    returning it if name==GRUB_DEFAULT
    1.if the value is not saved then check for double quotes, if it has 
        double quotes then it will be removed if not then (Missing ") will be added
    2.replace " >" with ">" to make sure it is found as invalid
    
    """
    
    if name not in available_conf_keys:
        raise ValueError("name not in available_conf_keys")
    
    if read_file is None:
        read_file=file_loc
    
    
    #check if last character is = to avoid possible bugs
    if name[-1] != '=':
        raise ValueError("name passed for get_value doesnt contain = as last character")

    with open(read_file) as file:
        data =file.read()
        lines=data.splitlines()
        
        # found the name that is being looked for in  a commented line
        found_commented=False
        
        val= None
        for line in lines:
            sline=line.strip()
            if  sline.find(f"#{name}")==0:
                found_commented=True
                comment_issue_string =f"{name} is commented out in {read_file}"
                
            if sline.find("#")==0:
                continue
            elif sline.find(name)==0:
                start_index= line.find(name)+len(name)
                
                val=sline[start_index:]
                
        #remove the double quotes in the end and the begining
        if name=="GRUB_DEFAULT=" and val is not None:
            if val.find(">")>0 and val.find(" >")==-1:
                val =val.replace(">"," >")
            elif val.find(" >")>0:
                #GRUB default is obviously invalid to make sure that other functions detect that its invalid lets just
                val.replace(" >",">")
                
            if val !="saved" :
                if val[0]=="\"" and val[-1]=='"':
                    val=val[1:-1]
                elif not val.replace(" >","").isdigit():
                    val+=" (Missing \")"
                
        
            
        if val is None:
            if found_commented and comment_issue_string not in issues:
                issues.append(comment_issue_string)
            else:
                issues.append(f"{name} was not found in {read_file}")
        if name=="GRUB_DISABLE_OS_PROBER=" and val is None:
            val="true"
        return val





def set_value(name,val,target_file=f'{CACHE_LOC}/temp.txt'):
    """ writes the changes to ~/.cache/grub-editor/temp.txt. call initialize_temp_file before start writing to temp.txt
    call self.saveConfs or cp the file from cache to original to finalize the changes
    
    Note: It does some minor edits to the value passed if name==GRUB_DEFAULT
    1.add double quotes if necessary
    2.replace " >" with ">"
    """

    if name[-1] != '=':
        raise ValueError("name passed for set_value doesn't contain = as last character")
    
    if name not in available_conf_keys:
        raise ValueError("name not in available_conf_keys")
    
    if name =="GRUB_DEFAULT=" and val!="saved":
        if val[0]!='"' and val[-1]!='"':
            val='"'+val+'"'
        if " >" in val:
            val= val.replace(" >",">")
    
    
    with open(target_file) as f:
        data=f.read()
        
    lines=data.splitlines()
    old_val=None
    for ind ,line in enumerate(lines):
        sline=line.strip()
        
        #no need to read the line if it starts with #
        if sline.find("#")==0:
            continue
        
        elif sline.find(name)==0:
            start_index= line.find(name)+len(name)
            old_val=line[start_index:]
            if old_val!="":
                new_line =line.replace(old_val,val)
                lines[ind]=new_line
            else:
                print("empty string")
                lines[ind]=name+val

    to_write_data=""
    
    for line in lines:
        to_write_data+=line+"\n"
    
    #if line wasn't found
    if old_val is None:
        to_write_data+=name+val
        
    with open(target_file,'w') as file:
        file.write(to_write_data)
        
def initialize_temp_file(file_path="/etc/default/grub"):
    """copies the file to ~/.cache/grub-editor/temp.txt so that set_value can start writing changes to it"""
    to_exec=f'cp \'{file_path}\' {CACHE_LOC}/temp.txt'
    print(to_exec)
    subprocess.run([to_exec],shell=True)
      


#stores the possible values of user preferences
preferences={"view_default":["on_the_application_itself","default_text_editor","None"],
             "create_snapshot":["add_changes_to_snapshot","None","ignore_changes"],
             "invalid_kernel_version":["fix","cancel","None"],
             "show_invalid_default_entry":["True","False","None"]
             }

def init_pref_file():
    """ Creates the preference file"""
    with open(f'{CONFIG_LOC}/main.json','w') as file :
        file.write(json.dumps({}))
        
def get_preference(key):
    # print('get pref  was called')
    
    #to avoid typos in string causing bugs
    if key not in preferences.keys():
        raise Exception("Key passed to the get_preference is not valid")
    
    subprocess.run([f'mkdir -p {CONFIG_LOC}/'],shell=True)
    
    if not os.path.exists(f'{CONFIG_LOC}/main.json'):
        # print("initializing preference file")
        init_pref_file()
        
    with  open(f'{CONFIG_LOC}/main.json') as file:
        try:
            data=file.read()
            # print(data,"data of the json file")
            if data !="":
                pref_dict =json.loads(data)
        except json.decoder.JSONDecodeError as e:
            printer(e)
            printer(traceback.format_exc())
            printer('This exception was handled with ease 😎')
            init_pref_file()
                
            
    #reopen the file and then read it
    with  open(f'{CONFIG_LOC}/main.json') as file:
        data=file.read()
        # print(data)
        if data!="":
            pref_dict =json.loads(data)
            try:
                value = pref_dict[key]
            except KeyError:
                set_preference(key,"None")
                value=None
        else:
            set_preference(key,"None")
            value=None
        if value=="None":
            value=None
        
    return value

def set_preference(key,value):
    print('set pref  was called')
    valid_key=False
    #to avoid typos in string causing bugs
    for  pref_key ,pref_val  in preferences.items():
        if key==pref_key:
            valid_key=True
            valid_val=False
            for possible_val in pref_val:
                if possible_val==value:
                    valid_val=True
                    break
            if not valid_val:
                raise Exception("Value passed to the set_preference is not valid")


    if not valid_key:
        raise Exception("Key passed to the get_preference is not valid")
    
    subprocess.run([f'mkdir -p {CONFIG_LOC}/'],shell=True)
    
    if os.path.exists(f'{CONFIG_LOC}/main.json'):
        with open(f'{CONFIG_LOC}/main.json') as file:
            try:
                pref_dict =json.load(file)
                pref_dict[key]=value
            except:
                init_pref_file()
                pref_dict={key:value}
        
        
    
    with open(f'{CONFIG_LOC}/main.json', "w") as pref_file:
    
        json.dump(pref_dict, pref_file, indent = 4)
    





def clear_layout(layout):
    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clear_layout(child.layout())

         
class Ui(QtWidgets.QMainWindow):
    resized = QtCore.pyqtSignal()
    snapshot_lbl_len_const=23
    
    
    def resizeEvent(self, event):
        """ resize event handler """
        self.resized.emit()
        return super(Ui, self).resizeEvent(event)
    
        
        
    def someFunction(self):
        self.createSnapshotList()
            
            
    def __init__(self):
        super(Ui, self).__init__()
        self.threadpool= QtCore.QThreadPool()
        uic.loadUi(f'{PATH}/ui/main.ui',self)
        
        
        # print('------------------------')
        
        #to make sure that Main window is unaccesible when a child window (QWidget) is open
        # self.setWindowModality(QtCore.Qt.ApplicationModal)

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
        
        #A list to store the invalid grub_default_entries
        self.invalid_entries=[]
        
        #dictionary for storing labels (rename) . key is index of the row
        self.btn_set.clicked.connect(self.btn_set_callback)
        self.rename_labels={}
        self.ledit_grub_timeout.setValidator(QtGui.QDoubleValidator())
        self.scrollAreaWidgetContents.adjustSize()
        self.VLayout_snapshot_parent.addStretch()
        
        #load the entries for available operating systems
        try:
            self.main_entries = find_entries()
        except GrubConfigNotFound:
            self.dialog_grub_cfg_not_found=DialogUi(False)
            dialog =self.dialog_grub_cfg_not_found
            dialog.setText("Grub config was not found at /boot/grub/grub.cfg."+
                "Please make sure grub is installed in this operating system."+
                " If grub is installed in another linux operating system then "+
                "grub.cfg would not be present in this operating system"+
                " and you will not be able to use grub editor from this operating system")
            dialog.removeCheckBox()
            dialog.show_dialog()
            dialog.exitOnAny()
            self.setEnabled(False)
            return
        
        except PermissionError:
            
            def change_permission():
                subprocess.run(["pkexec chmod 666 /boot/grub/grub.cfg"],shell=True)
            
            def btn_ok_callback():
                worker=self.startWorker(change_permission)
                worker.signals.finished.connect(on_finish)
            
            def on_finish():
                QtCore.QCoreApplication.quit()
                status = QtCore.QProcess.startDetached(sys.executable, sys.argv)
                print(status)
            
            self.dialog_cfg_permission=DialogUi(True)
            dialog=self.dialog_cfg_permission
            dialog.setText("Permission error occured while trying to read /boot/grub/grub.cfg. "+
                           "Please make sure /boot/grub/grub.cfg is readable by the current user."+
                           "Grub Editor can change the file permission for you if you want")
            dialog.show_dialog()
            dialog.btn_ok.clicked.connect(btn_ok_callback)
            dialog.setBtnOkText("Change permission")
            dialog.removeCheckBox()
            dialog.exitOnCancel()
            dialog.exitOnClose()
            self.setEnabled(False)
            return
        
        # except Exception as e:
        #     self.error_dialog=ErrorDialogUi()
        #     self.error_dialog.set_error_title(str(e))
        #     self.error_dialog.set_error_body(traceback.format_exc())
        #     self.error_dialog.exitOnAny()
        #     self.error_dialog.show()
        #     self.setEnabled(False)
        #     return

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
        
        
        self.original_modifiers=[]
        self.modified_original =False
        
        self.setUiElements(show_issues=True)
        
        
        self.comboBox_configurations.currentIndexChanged.connect(self.comboBox_configurations_callback)
        if len(self.issues) > 0:
            self.issuesUi=IssuesUi(self.issues)
            self.issuesUi.show()
            self.setEnabled(False)
            
            def quit_():
                sys.exit()
                
            def open_file():
                subprocess.run(["xdg-open /etc/default/grub"],shell=True)
                sys.exit()
                
            self.issuesUi.btn_quit.clicked.connect(quit_)
            self.issuesUi.btn_open_file.clicked.connect(open_file)
        self.ledit_grub_timeout.textChanged.connect(self.ledit_grub_timeout_callback)
        self.predefined.toggled.connect(self.radiobutton_toggle_callback)
        self.comboBox_grub_default.currentIndexChanged.connect(self.comboBox_grub_default_on_current_index_change)
        self.checkBox_boot_default_entry_after.toggled.connect(self.checkBox_boot_default_entry_after_on_toggle)
        self.checkBox_show_menu.toggled.connect(self.checkBox_show_menu_on_toggle)
        self.btn_reset.clicked.connect(self.btn_reset_callback)
        self.checkBox_look_for_other_os.clicked.connect(self.checkBox_look_for_other_os_callback)

        




    def ledit_grub_timeout_callback(self):
        value =get_value('GRUB_TIMEOUT=',self.issues)
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
        timeout=get_value('GRUB_TIMEOUT=',self.issues)
        if  timeout !=None and timeout !='-1':
            # printer(timeout)
            if self.checkBox_boot_default_entry_after.isChecked():
                if btn  in self.original_modifiers:
                    self.original_modifiers.remove(btn)
            else:
                if btn not in self.original_modifiers:
                    self.original_modifiers.append(btn)

        elif (timeout == None or timeout =='-1' ) :
            if self.checkBox_boot_default_entry_after.isChecked():
                if btn  not in self.original_modifiers:
                    self.original_modifiers.append(btn)
            else:
                if btn   in self.original_modifiers:
                    self.original_modifiers.remove(btn)

        self.handle_modify()

    def btn_reset_callback(self):
        """ on clicked callback for reset button """


        self.comboBox_configurations.setCurrentIndex(0)
        
        


    def checkBox_show_menu_on_toggle(self):
        """ on toggled handler for checkBox_show_menu """

        timeout_style = get_value('GRUB_TIMEOUT_STYLE=',self.issues)
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

    def comboBox_configurations_callback(self,value):
        global file_loc
        # printer(self.configurations[value],'load configuration from callback')
        value =self.configurations[value]
        if value ==GRUB_CONF_LOC:
            file_loc=GRUB_CONF_LOC
        else:
            file_loc=f'{DATA_LOC}/snapshots/{value}'
        
        self.setUiElements(show_issues=True)
            
        
        
    def btn_add_callback(self):
        value = self.ledit_grub_timeout.text()
        value =float(value)
        self.ledit_grub_timeout.setText(str(value+1))
        value =get_value('GRUB_TIMEOUT=',self.issues)
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
        
        value =get_value('GRUB_TIMEOUT=',self.issues)
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

    def handle_invalid_default_entry(self,invalid_value):
        pref_show = get_preference("show_invalid_default_entry")
        
        def create_win():
            ''' Creates a window to show that the grub default has an invalid default entry '''
                # print(btn_cancel)
            self.dialog_invalid_default_entry=DialogUi(btn_cancel=False)
            self.dialog_invalid_default_entry.label.setText(f"{file_loc} currently has an invalid default entry")
            self.dialog_invalid_default_entry.show()
            self.dialog_invalid_default_entry.raise_()
            self.dialog_invalid_default_entry.activateWindow()
            
            
        def set_kernel_version_fixer(crct_value):
            ''' Adds the fix btn to the invalid_default_entry_dialog or does the action preffered by
            the user pereference file'''
            pref_fix = get_preference("invalid_kernel_version")
            
            def fix(read_checkbox=True):
                ''' Fixes the invalid entry '''
                
                print('editing the file from',file_loc,'to fix kernel version')
                # print(value,'value--------------------------')

                if file_loc ==GRUB_CONF_LOC:
                    initialize_temp_file(file_loc)
                    set_value("GRUB_DEFAULT=",crct_value)
                    self.saveConfs()
                else:
                    set_value('GRUB_DEFAULT=',crct_value,target_file=file_loc)
                
                if read_checkbox and dwin.checkBox.isChecked():
                    set_value("invalid_kernel_version","fix")
                
                dwin.close()
                
            if pref_fix==None:
                dwin = self.dialog_invalid_default_entry
                dwin.btn_ok.setText('Fix')
                dwin.checkBox.setText("Do this everytime")
                dwin.resize(500,180)
                
                if file_loc ==GRUB_CONF_LOC:
                    file_name = GRUB_CONF_LOC
                    dwin.label.setText(f'{file_name} currently has an invalid default entry. It is because of a kernel update . Do you want Grub editor to fix it for you?')
                    
                elif f'{DATA_LOC}/snapshots/' in  file_loc:
                    file_name=file_loc.replace(f'{DATA_LOC}/snapshots/','')
                    dwin.label.setText(f'snapshot you selected ({file_name}) currently has an invalid default entry. It is because of a kernel update . Do you want Grub editor to fix it for you?')
                    
                else:
                    printer("Error unknown condition when checking file_loc")
                    printer(file_loc)
                    self.error_dialog=ErrorDialogUi()
                    self.error_dialog.set_error_title("Error unknown condition when checking file_loc")
                    self.error_dialog.set_error_body("file_loc : "+file_loc)
                    self.error_dialog.show()
                
                
                    
                def cancel(read_checkbox=True):
                    if read_checkbox and dwin.checkBox.isChecked():
                        set_value("invalid_kernel_version","cancel")
                    dwin.close()
                dwin.add_btn_cancel()
                dwin.btn_ok.clicked.connect(fix)
                dwin.btn_cancel.clicked.connect(cancel)
                
            elif pref_fix=="fix":
                fix()
            elif pref_fix=="cancel":
                #Program actually doesnt have to do anything it its cancel so...
                pass
        
        #find out if created a unique dialog_window
        # unique_dialog_win= False
        # print(unique_dialog_win,'unique_dialog_win')
        crct_value= None
        index = invalid_value.find('(Kernel: ')
        try:
            for value in self.all_entries:
                
                #check if the part before the kernel is same
                if invalid_value[:index]== value[:index]:
                    
                    pattern=r'\d.\d+'
                    krnl_major_vrsn=re.search(pattern,invalid_value).group(0)
                    krnl_major_vrsn2 = re.search(pattern,value).group(0)
                    # print(value ,krnl_major_vrsn2,krnl_major_vrsn)
                    if krnl_major_vrsn2 == krnl_major_vrsn:
                        
                        #if the invalid contains fallback then the non invalid should also contain initramfs
                        condition =  not ( ('fallback initramfs)' in value ) ^ ('fallback intramfs)' in invalid_value ) )
                        
                        #to avoid some unexpected behavior by python
                        # first =('fallback initramfs)' in value )
                        # second = ('fallback initramfs)' in invalid_value )
                        
                        # condition = not (first ^ second)
                        
                        if condition and (value != invalid_value):
                            # print('the right one ',invalid_value,value)
                            crct_value =value
                            break
                        
        except AttributeError as e:
            printer("invalid default entry is not fixable")
            # printer(traceback.format_exc())
            
        if pref_show==None:
            create_win()
            
        if crct_value != None:
            set_kernel_version_fixer(crct_value)
        
            
        self.set_comboBox_grub_default_style()
        
    def set_comboBox_grub_default_style(self):
        
        ''' Sets the correct style for comboBox_grub_default by checking 
        if the current entry is invalid or not '''
        
        self.comboBox_grub_default_invalid_style="""QComboBox {
background: #ff5145;
color:black;
}"""
        current_is_invalid=False
        for entry in self.invalid_entries:
            if entry == self.all_entries[self.comboBox_grub_default.currentIndex()]:
                self.comboBox_grub_default.setStyleSheet(self.comboBox_grub_default_invalid_style)
                current_is_invalid=True
                break
        if not current_is_invalid:
            self.comboBox_grub_default.setStyleSheet("")
    
    def get_g_default_from_number(self,g_default:str):
        ''' Argument could be in 1 >2 format or just plain number like 0 '''
        sub_ptrn=r"\d >\d"
        match = re.search(sub_ptrn,g_default)
        
        #to avoid anyother format than "1 >2"
        if len(g_default)==4 ^ len(g_default)==1:
            return None
        if match is not None:
            try:
                main_entry_obj = self.main_entries[int(g_default[0])]
                sub_entry_obj= main_entry_obj.sub_entries[int(g_default[3])]
                entry= main_entry_obj.title+" >"+sub_entry_obj.title
                
                return entry
            except IndexError:
                return None
        
        elif g_default.isdigit():
            main_entry_obj = self.main_entries[int(g_default[0])]
            entry= main_entry_obj.title
            if "Advanced options for " in entry:
                entry= main_entry_obj.title+" >"+main_entry_obj.sub_entries[0].title
            return entry
    
        else:
            return None
            
    
    
    def set_comboBox_grub_default(self,show_invalid_default=False):
        """ sets the right index to comboBox_grub_default and radio buttons,
        if second argument is true then it will check if the grub default value is invalid and if it is invalid it will show a dialog"""
        
        grub_default_val =get_value('GRUB_DEFAULT=',self.issues)
    
        
        if grub_default_val=='saved':
            self.previously_booted_entry.setChecked(True)
            # self.comboBox_grub_default.setCurrentIndex(0)
        elif grub_default_val==None:
            self.previously_booted_entry.setChecked(False)
            self.predefined.setChecked(False)
        else:
            self.predefined.setChecked(True)
            
            # # If grub_default doesnt contain double quotation marks as the first and last character then it is an invalid entry
            # if not is_vld_g_default(grub_default_val):
            #     self.handle_invalid_default_entry(grub_default_val)
            #     return None

            
            try:
                
                if grub_default_val in self.invalid_entries:
                    self.handle_invalid_default_entry(grub_default_val)
                self.comboBox_grub_default.setCurrentIndex(self.all_entries.index(grub_default_val))    
                
            except ValueError:
                #not really invalid as it could be a number
                invalid_value=get_value('GRUB_DEFAULT=',self.issues)
                
                from_number =self.get_g_default_from_number(invalid_value)
                if  from_number  != None:
                    index = self.all_entries.index(from_number)
                    self.comboBox_grub_default.setCurrentIndex(index)
                    
                    #to make sure that the code below is not executed
                    return None

                
                #concistency iun showing entries
                # invalid_value= invalid_value.replace(">"," >")
                
                #check if it already exists in the grub_default comboBox
                if invalid_value not in self.all_entries:
                    
                    self.comboBox_grub_default.addItem(invalid_value)
                    model =self.comboBox_grub_default.model()
                    self.all_entries.append(invalid_value)
                    self.invalid_entries.append(invalid_value)
                    model.setData(model.index(len(self.all_entries)-1, 0), QtGui.QColor("#ff5145"), QtCore.Qt.BackgroundRole)
                    model.setData(model.index(len(self.all_entries)-1, 0), QtGui.QColor("black"), QtCore.Qt.ForegroundRole)
                    self.comboBox_grub_default.setCurrentIndex(len(self.all_entries)-1)
                else:
                    raise Exception("Unexpected case when processing invalid GRUB_DEFAULT value")
                self.handle_invalid_default_entry(invalid_value)
                
                



                
    def setUiElements(self,show_issues=True,only_snapshots=False):
        """reloads the ui elements that should be reloaded
            when show issues is true it will show a dialog if the grub default value is invalid
        
        """
        if not only_snapshots:
            try:
                #catch error that might occur when self.configurations is not initialized
                index =self.comboBox_configurations.currentIndex()
            except AttributeError:
                pass

            finally:

                timeout=get_value('GRUB_TIMEOUT=',self.issues)
                if  timeout !=None and timeout!='-1':
                    # printer(timeout)
                    self.ledit_grub_timeout.setText(timeout)
                else:
                    self.checkBox_boot_default_entry_after.setChecked(False)



        #stores the available configuration files
        self.configurations=[GRUB_CONF_LOC]
        
        #add the available configurations to the combo box
        contents = subprocess.check_output([f'ls {DATA_LOC}/snapshots/'],shell=True).decode()
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
        if file_loc==GRUB_CONF_LOC:
            self.comboBox_configurations.setCurrentIndex(0)
        elif '/snapshots/' in file_loc:
            index = file_loc.index('/snapshots/')
            
            #11 is the length of /snapshots/ part
            snapshot_name= file_loc[index+11:]
            
            index=self.configurations.index(snapshot_name)
            
            self.comboBox_configurations.setCurrentIndex(index)
            

        # printer('added all items to combo box configurations')
        self.comboBox_configurations.blockSignals(False)
        
        if not only_snapshots:
            if get_value('GRUB_TIMEOUT_STYLE=',self.issues)=='hidden':
                self.checkBox_show_menu.setChecked(False)
            elif get_value('GRUB_TIMEOUT_STYLE=',self.issues)=='menu':
                self.checkBox_show_menu.setChecked(True)

            
                
            if get_value('GRUB_TIMEOUT=',self.issues)=='-1' or get_value('GRUB_TIMEOUT=',self.issues)==None:
                self.checkBox_boot_default_entry_after.setChecked(False)
            else:
                self.checkBox_boot_default_entry_after.setChecked(True)
                
            self.comboBox_grub_default.blockSignals(True)
            self.set_comboBox_grub_default(show_invalid_default=show_issues)
            self.comboBox_grub_default.blockSignals(False)
            
        self.createSnapshotList()

        if not only_snapshots:
            #set the value of checkBox_look_for_other_os
            #passing an empty string it isnt as issue if GRUB_DISABLE_OS_PROBER is commented or not found
            value = get_value('GRUB_DISABLE_OS_PROBER=',[])
            
            #single ,double quotes work 
            value =remove_quotes(value)
            
            if value=="false":
                self.checkBox_look_for_other_os.setChecked(True)
            elif value=="true":
                self.checkBox_look_for_other_os.setChecked(False)
            else:
                # raise Exception("Unknown value for GRUB_DISABLE_OS_PROBER",value)
                printer(f"Unknown value for GRUB_DISABLE_OS_PROBER {value} in {file_loc}")
                self.error_dialog=ErrorDialogUi()
                self.error_dialog.set_error_body(f"function SetUiElements: Unknown value for GRUB_DISABLE_OS_PROBER {value} in {file_loc}")
                self.error_dialog.resize(800,300)
                self.error_dialog.show()
                
        if not only_snapshots:
            self.original_modifiers=[]
        self.handle_modify()
        self.set_comboBox_grub_default_style()
        
        
    def set_lbl_details(self):
        """receives the string in lbl_details_text and sets it as the label for lbl_details"""
        try:
            self.lbl_details.setText(self.lbl_details_text)
        except RuntimeError:
            #this could fail because of two reasons 
            #1.lbl_details hasnt yet been created
            #2.it was deleted
            pass
        except AttributeError:
            pass
        
    def saveConfsToCache(self):
        """ saves the configurations that are in GUI to cache ~/.grub-editor/temp.txt  """
        self.lbl_details_text=''
        
        # clear the file in cache
        subprocess.run([f'rm {CACHE_LOC}/temp.txt'],shell=True)
        subprocess.run([f'mkdir -p {CACHE_LOC}'],shell=True)
        subprocess.run([f'touch {CACHE_LOC}/temp.txt'],shell=True)

        index =self.comboBox_configurations.currentIndex()
        total=len(self.configurations)
        if index ==0 or (index==total-1 and "(modified)" in self.configurations[-1]):
            target_file_copy = GRUB_CONF_LOC
        else:
            target_file_copy =f'{DATA_LOC}/snapshots/'+self.configurations[index]

        initialize_temp_file(target_file_copy)
        
        if self.checkBox_show_menu.isChecked():
            set_value('GRUB_TIMEOUT_STYLE=','menu')
        else:
            set_value('GRUB_TIMEOUT_STYLE=','hidden')
        
        # printer('save condfs to cache was called')
        if self.predefined.isChecked():
            # printer('predefined is checked')
            self.grub_default =str(self.comboBox_grub_default.currentText())

            if self.grub_default.count('>') <=1:

                if '>' in self.grub_default:
                    front_part=self.grub_default[:self.grub_default.find(' >')]
                    last_part=self.grub_default[self.grub_default.find('>'):]
                    to_write=front_part+last_part
                    set_value('GRUB_DEFAULT=',to_write)
                    # printer('called:''GRUB_DEFAULT=',to_write)
                    # printer(to_write+'part to be written')
                else:
                    set_value('GRUB_DEFAULT=','\"'+self.grub_default+'\"')
                    # printer('called:''GRUB_DEFAULT='+'\"'+self.grub_default+'\"')
                    # printer('woke from 20 sec sleep')
                #set the value of grub_default
            else:
                printer('Error occured when setting grub default as combobox text has more than one  1\' >\'  ')
                self.lbl_status.setText('Error occured when setting grub default as combobox text has more than one  1\' >\'  ')
                printer(self.grub_default)
        elif self.previously_booted_entry.isChecked():
            # printer('i\'m not Supposed to be printed')
            set_value('GRUB_DEFAULT=','saved')

        if self.checkBox_boot_default_entry_after.isChecked():
            set_value('GRUB_TIMEOUT=',self.ledit_grub_timeout.text())
            # printer('setting grub-timeout')

        else:
            set_value('GRUB_TIMEOUT=','-1')
            # printer('setting grub-timeout -1')

        #look for other os
        if self.checkBox_look_for_other_os.isChecked():
            set_value("GRUB_DISABLE_OS_PROBER=","false")
        else:
            set_value("GRUB_DISABLE_OS_PROBER=","true")
            
    def set_conf_and_update_lbl_details(self):
        try:
            if "update-grub" in os.listdir( "/usr/bin/"):
                to_exec=f' pkexec sh -c \'echo \"authentication completed\"  && \
                        cp -f  "{CACHE_LOC}/temp.txt"  '+GRUB_CONF_LOC +' && sudo update-grub 2>&1 \'  '
                # print(to_exec)
                process = subprocess.Popen([to_exec],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True)
            else:
                process = subprocess.Popen([f' pkexec sh -c \'echo \"authentication completed\"  && \
                        cp -f  "{CACHE_LOC}/temp.txt"  '+GRUB_CONF_LOC +' && grub-mkconfig -o /boot/grub/grub.cfg 2>&1 \'  '],
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
                    try:
                        self.vBar.setValue(self.vBar.maximum())
                    except AttributeError:
                        #because vBar is not initialized yet
                        pass
                        
                    except RuntimeError:
                        #because vBar is deleted
                        pass
                    
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
                        except RuntimeError:
                            pass
                break


            if not authentication_error:
                self.lbl_status.setText('Saved successfully')
            else:
                self.lbl_status.setText('Authentication error occured')
                self.lbl_status.setStyleSheet('color: red')
                    
        except Exception as e:
            printer(e)
            printer('error trying to save the configurations')
            print("----------------------------")
            printer(traceback.format_exc())
            self.lbl_status.setText('An error occured when saving')
            self.lbl_status.setStyleSheet('color: red')
            print(DEBUG,"DEBUG value")
            if DEBUG:
                print("raising exception inside the function")
                # pytest.fail("Caught error in set_conf_and_update_lbl_details")
                raise e
            else:
                print(DEBUG,"DEBUG")
            
    def onSaveConfsFinish(self):
        self.setUiElements(show_issues=False)
        self.HLayout_save.itemAt(1).widget().deleteLater()
        self.loading_bar.setParent(None)

    def saveConfs(self):
        """ copies the configuration file from cache to the /etc/default/grub
            It is not useful to call this function if editing target doesnt require root privilages
            as you can just use set_value to set any value directly
        """
        self.show_saving()

        
        #the variable will be used for testing purposes
        self.loading_bar =LoadingBar()
        insert_into(self.HLayout_save,1,self.loading_bar)
        self.saveConfs_worker=self.startWorker(self.set_conf_and_update_lbl_details,self.onSaveConfsFinish,None)
        

    def checkBox_look_for_other_os_callback(self):
        """ callback handler for checkBox_look_for_other_os
            reacts to modifications
        """
        value=get_value("GRUB_DISABLE_OS_PROBER=",self.issues)
        value=remove_quotes(value)
        
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
        if preference==None and len(self.original_modifiers)>0:
            self.create_snapshot_dialog = CreateSnapshotUi()
            self.create_snapshot_dialog.btn_ignore_changes.clicked.connect(self.btn_ignore_changes_callback)
            self.create_snapshot_dialog.btn_add_changes_to_snapshot.clicked.connect(self.btn_add_changes_to_snapshot_callback)
            self.create_snapshot_dialog.show() 
        elif preference=='add_changes_to_snapshot':
            self.saveConfsToCache()
            # printer('saving from cache')
            self.createSnapshot(from_cache=True)
        elif preference=='ignore_changes' or preference ==None:
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
            subprocess.Popen([f'touch {DATA_LOC}/snapshots/{date_time}'],shell=True)
            with open(f'{DATA_LOC}/snapshots/{date_time}','w') as file:
                file.write(data)
        else:
            # printer('created a snapshot grom cache')
            to_execute=f'cp {CACHE_LOC}/temp.txt {DATA_LOC}/snapshots/{date_time}'
            # print(to_execute)
            subprocess.run([to_execute],shell=True)
        self.setUiElements(only_snapshots=True)
        self.handle_modify()
        # print('setUi elems was called')



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
            self.vBar=self.scrollArea.verticalScrollBar()
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
                    target_wid=self.verticalLayout_2.itemAt(i).widget()
                    target_wid.setParent(None)
                    target_wid.deleteLater()
                    break

                
            btn.setText('Show Details')
            
    def show_saving(self):
        if not (self.verticalLayout_2.itemAt(1) and isinstance(self.verticalLayout_2.itemAt(1),QtWidgets.QHBoxLayout)):
    
            #create a label to show user that saving
            self.lbl_status= QtWidgets.QLabel()
            self.lbl_status.setText('Waiting for authentication')
            self.lbl_status.setStyleSheet('color:#03fc6f;')
            
            
            
            # self.verticalLayout.addWidget(self.lbl_status)
            
            # create a button (show details)
            self.btn_show_details= QtWidgets.QPushButton()
            self.btn_show_details.setText('Show Details')
            self.btn_show_details.clicked.connect(partial(self.btn_show_details_callback,'edit_configurations'))
            
            #create a horizontal layout
            self.HLayout_save= QtWidgets.QHBoxLayout()
            self.HLayout_save.setContentsMargins(6,0,6,0)
            self.HLayout_save.setObjectName('HLayout_save')
            self.HLayout_save.addWidget(self.lbl_status)
            self.HLayout_save.addWidget(self.btn_show_details)
            self.verticalLayout_2.addLayout(self.HLayout_save)
            
            
            
        else:
            self.lbl_status.setText('Waiting for authentication')
            self.lbl_status.setStyleSheet('color:#03fc6f;')
            
            
    def btn_set_callback(self,unsafe=False):
        
        """ if argument is true then it checks configurations for recommendations and errors """

        self.recommendations=[]
        self.recmds_fixes=[]
        grub_timeout_value=self.ledit_grub_timeout.text()
        
        if self.checkBox_boot_default_entry_after.isChecked() and grub_timeout_value=='0':
            # self.ledit_grub_timeout.setText('Use 0.0 instead of 0 ')
            # self.ledit_grub_timeout.selectAll()
            # self.ledit_grub_timeout.setFocus()
            self.recommendations.append('If you are doing dual boot it is preferred to use 0.0 instead of 0 as timeout')
            def temp():
                self.ledit_grub_timeout.setText('0.0')
            self.recmds_fixes.append(temp)


       
        
        
        
        # self.show_saving()
        # printer(interrupt,'interrupt')
        if not unsafe:
            if  len(self.recommendations)==0:
                self.saveConfsToCache()
                self.saveConfs()
            if len(self.recommendations)>0:
                self.set_recommendations_window=SetRecommendations(self.recommendations,self.recmds_fixes)
                self.set_recommendations_window.show()
        else:
            self.saveConfsToCache()
            self.saveConfs()

            

    # def btn_show_orginal_callback(self):
    #     global file_loc
    #     file_loc=GRUB_CONF_LOC
    #     self.sender().parent().deleteLater()
    #     self.setUiElements()

            
    
    def btn_view_callback(self,snapshot_name):
        try:
            new_loc= f'{DATA_LOC}/snapshots/'+snapshot_name
            view_default=get_preference('view_default')
            self.view_btn_win =ViewButtonUi(new_loc)
            
            if view_default==None:
                self.view_btn_win.show()
                
            elif view_default=='on_the_application_itself':
                
                self.view_btn_win.btn_on_the_application_itself_callback()
                
            elif view_default=='default_text_editor':
                self.view_btn_win.btn_default_text_editor_callback()
                
            else:
                printer('ERROR: unknown value for view_default on main.json',view_default)
                
        except Exception as e:
            if DEBUG:
                raise e
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
                    self.lbl_status.setText('Waiting for authentication')
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
                    # self.show_saving()
                self.set_snapshot_worker=self.startWorker(self.update_lbl_status,self.setUiElements,None,line)
                if self.dialog_invalid_default_entry :
                    self.dialog_invalid_default_entry.close()
                


            #check if snapshot's default os is a valid one 
            default=get_value("GRUB_DEFAULT=",self.issues,f"{DATA_LOC}/snapshots/{line}")

            if default not in self.all_entries:
                # printer("Value of default in snapshot is not a valid os")
                # printer(default ,'is the value found in snapshot')
                # printer(self.all_entries)
                self.dialog_invalid_snapshot=DialogUi(btn_cancel=True)
                self.dialog_invalid_snapshot.setText("The snapshot you have selected has an invalid value for grub default")
                self.dialog_invalid_snapshot.setBtnOkText('continue anyway')
                self.dialog_invalid_snapshot.show()
                self.dialog_invalid_snapshot.btn_ok.clicked.connect(set_snapshot)

            else:
                set_snapshot()
                


            # printer(f'pkexec sh -c  \' cp -f  "{DATA_LOC}/snapshots/{line}" {write_file} && sudo update-grub  \' ')

            
        except Exception as e:
            printer(traceback.format_exc())
            printer(str(e))
            printer('Error occured in btn_set_snapshot')

    

    def startWorker(self,toCall,onFinish=None,onResult=None,*args):
        """ arguments are funtion to run , funtion to call when finishes ,function to call with result if no errors occured, 
            arugments of the first funtion 
            return the worker object for testing needs"""
            
        def handleWorkerException(exception:Exception):
            if DEBUG:
                raise exception
            
        try:
            
            worker = Worker(toCall,*args)
            if onFinish is not None:
                worker.signals.finished.connect(onFinish)
                # print("connected onFInish",onFinish==self.setUiElements)
            if onResult is not None:
                worker.signals.result.connect(onResult)
            worker.signals.exception.connect(handleWorkerException)
            self.threadpool.start(worker)
            
            return worker
        except Exception as e:
            if DEBUG:
                print("raising exception")
                raise e
            printer(traceback.format_exc())
            printer(str(e))
        
    def update_lbl_status(self,line):
        try:
            if "update-grub" in os.listdir( "/usr/bin/"):
                to_execute=f'pkexec sh -c  \' cp -f  "{DATA_LOC}/snapshots/{line}" {write_file} && update-grub  \' '
                # print(to_execute)
                process = subprocess.Popen([to_execute], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
            else:
                to_exec=f'pkexec sh -c  \' cp -f  "{DATA_LOC}/snapshots/{line}" {write_file} && grub-mkconfig -o /boot/grub/grub.cfg  \' '
                process = subprocess.Popen([to_exec], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,shell=True)
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
                    try :
                        self.vBar.setValue(self.vBar.maximum())
                    except AttributeError:
                        pass
                        #because vBar is not initialized yet
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
                        except RuntimeError:
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
            
            
            
    def btn_delete_callback_creator(self,arg):
        def func():
            cmd =f'rm \'{DATA_LOC}/snapshots/{arg}\''
            # printer(string)
            subprocess.Popen([cmd],shell=True)
            global file_loc
            if file_loc == f'{DATA_LOC}/snapshots/{arg}':
                file_loc=GRUB_CONF_LOC
                if self.verticalLayout.itemAt(3):
                    self.verticalLayout.itemAt(3).widget().deleteLater()
            self.setUiElements(only_snapshots=True)
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
                subprocess.Popen([f'mv \'{DATA_LOC}/snapshots/{line}\' \'{DATA_LOC}/snapshots/{text}\' '],shell=True)
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
        
        
        

    

    def comboBox_grub_default_on_current_index_change(self,value):
        """ current index changed callback """
        
        try:
            # printer('combo box currentIndexChanged')
            self.set_comboBox_grub_default_style()
            
                
            
            comboBox = self.sender()
            combo_text =self.all_entries[comboBox.currentIndex()]
            grub_default = get_value('GRUB_DEFAULT=',self.issues)
            current_conf=self.configurations[self.comboBox_configurations.currentIndex()]
            if grub_default !=combo_text and not "(modified)" in current_conf:
                # self.modified_original = True
                if comboBox not in self.original_modifiers:
                    self.original_modifiers.append(self.sender())
                # printer(grub_default,combo_text)
            elif grub_default ==combo_text:
                if comboBox in self.original_modifiers:
                    self.original_modifiers.remove(comboBox)
            self.handle_modify()
        except Exception as e:
            printer(traceback.format_exc())
            printer(str(e))


    def get_radiobutton_predefined(self):
        """returns the value radio button predefined should have now"""
        
        
    def radiobutton_toggle_callback(self):
        btn= self.sender()
        
        if btn.text()=='predefined:':
            # printer('yes')
            default_entry =get_value('GRUB_DEFAULT=',self.issues)
            # printer('grub_default')
            if (default_entry !='saved' and default_entry !=None) and btn.isChecked():
                if btn  in self.original_modifiers:
                    self.original_modifiers.remove(btn)  
                # printer('1st')  
            elif (default_entry =='saved' or default_entry ==None) and not btn.isChecked():
                if btn in self.original_modifiers:
                    self.original_modifiers.remove(btn)
                # printer('2nd')
            else:
                # printer('last')
                if btn not in self.original_modifiers:
                    self.original_modifiers.append(btn)
        else:
            raise Exception("Unexpected  radiobutton callback")
        self.handle_modify()


    def handle_modify(self):
        # print(self.original_modifiers)
        """ handles when the loaded configuration is modified in the apps . 
        it adds "(modified)" to the value of comboBox_configurations  according to the length of self.original_modifiers""" 
        try:
            current_item = self.configurations[self.comboBox_configurations.currentIndex()]
            # print(current_item+':current_item')
            # if current_item==GRUB_CONF_LOC or current_item=='/etc/default/grub(modified)':
            
            # print('yes')
            if len(self.original_modifiers)>0:
                # print(self.original_modifiers)
                # printer(current_item)
                self.btn_reset.setEnabled(True)
                self.btn_set.setEnabled(True)
                if '(modified)' not in current_item:
                    stringy=current_item+'(modified)'
                    self.comboBox_configurations.blockSignals(True)
                    self.comboBox_configurations.addItem(stringy)
                    self.configurations.append(stringy)
                    self.comboBox_configurations.setCurrentIndex(self.comboBox_configurations.count()-1)
                    self.comboBox_configurations.blockSignals(False)
            else:
                self.btn_reset.setEnabled(False)
                if GRUB_CONF_LOC in self.configurations[self.comboBox_configurations.currentIndex()]:
                    self.btn_set.setEnabled(False)
                else:
                    self.btn_set.setEnabled(True)
                
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
        except Exception as e:
            printer(traceback.format_exc())
            printer(str(e))
        
        
    def createSnapshotList(self):
        try:
            contents = subprocess.check_output([f'ls {DATA_LOC}/snapshots/'],shell=True).decode()
            self.lines =contents.splitlines()

            self.HLayouts_list=[]
            number =0
            clear_layout(self.VLayout_snapshot)

            reconnect(self.btn_create_snapshot.clicked,self.btn_create_snapshot_callback)
            if len(self.lines) >0 and  self.lbl_no_snapshots:
                self.lbl_no_snapshots.setText('Snapshots are backups of /etc/default/grub .Snapshots can help you when you mess up some configuration in /etc/default/grub . These snapshots are stored inside ~/.grub-editor/snapshots/')
                
            elif len(self.lines) ==0 :
                printer('lines are zero and label wasnt found soo.. creating that lbl_nosnapshots')
                self.lbl_no_snapshots.setText('Looks like you dont have any snapshots .Snapshots are backups of /etc/default/grub .Snapshots can help you when you mess up some configuration in /etc/default/grub . These snapshots are stored inside ~/.grub-editor/snapshots/')
                self.lbl_no_snapshots.setWordWrap(True)
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
                self.pushButton_3.clicked.connect(self.btn_delete_callback_creator(line))
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
        global file_loc
        file_loc= self.file_location
        MainWindow.setUiElements(show_issues=False)
        MainWindow.tabWidget.setCurrentIndex(0)
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
        
        
        
        
        
        for i,recommendation in recommendations_list:
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
        MainWindow.btn_set_callback(unsafe=True)
        MainWindow.set_recommendations_window.close()

    def btn_fix_all_callback(self):
        for fix in self.fixes_list:
            fix()
        MainWindow.btn_set_callback()
        MainWindow.set_recommendations_window.close()


    def btn_fix_callback_creator(self,HLayout,fix,verticalLayout_2):
        """ first argument is the HorizontalLayout of button and second argument is the function that fixes the issue
        and the third the the vertical layout where these horizontal layout are located"""
        def btn_fix_callback(self):
            fix()
            clear_layout(HLayout)
            if verticalLayout_2.count() == 0:
                MainWindow.set_recommendations_window.close()
                MainWindow.btn_set_callback()

        return btn_fix_callback


def main():
    
    global app
    app =QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('/usr/share/pixmaps/grub-editor.png'))
    global MainWindow
    MainWindow=Ui()
    sys.exit(app.exec_())

if __name__ =='__main__':
    main()