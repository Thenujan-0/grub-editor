import os
import subprocess

from PyQt5 import  uic
from PyQt5.QtWidgets import QDesktopWidget, QDialog


PATH = os.path.dirname(os.path.realpath(__file__))

class ViewModePopup(QDialog):
    def __init__(self,file_location,conf_handler,parent):
        self.file_location = file_location
        self.conf_handler = conf_handler
        self.parent = parent
        super(ViewModePopup, self).__init__(parent)
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
        self.conf_handler.current_file= self.file_location
        self.parent.setUiElements(show_issues=False)
        self.parent.tabWidget.setCurrentIndex(0)
        self.safe_close('on_the_application_itself')