from PyQt5 import QtWidgets,uic,QtCore
import unittest
class TestFunctions():
    def click_button(self,widget):
        
        widget.click()
        
    def call_function(self,function_string):
        exec(function_string)

    
    