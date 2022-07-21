from main import DialogUi

def test_setTextBtn(qtbot):
    mw=DialogUi()
    qtbot.addWidget(mw)
    
    mw.setText("hey there")
    assert mw.label.text()=="hey there"
    
    mw.setBtnOkText("Not ok")
    assert mw.btn_ok.text()=="Not ok"

