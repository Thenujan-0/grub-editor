
import os
import sys

from PyQt5 import QtWidgets,QtCore

from grubEditor import main

def test_invalid_default_entry(qtbot):
    mw=main.Ui()
    main.MainWindow=mw
    
    
    
