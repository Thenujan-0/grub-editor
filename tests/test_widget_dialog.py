import os
import sys
from pathlib import Path


PATH = os.path.dirname(os.path.realpath(__file__))
#get the parent directory
PATH = Path(PATH).parent
sys.path.append(PATH)


import main

def test_setTextBtn(qtbot):
    mw=main.DialogUi()
    qtbot.addWidget(mw)
    
    mw.setText("hey there")
    assert mw.label.text()=="hey there"
    
    mw.setBtnOkText("Not ok")
    assert mw.btn_ok.text()=="Not ok"

