# import unittest

# import os,sys,inspect


# #stolen from stackoverflow or grepperchrome
# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# sys.path.insert(0,parentdir) 


# import main
# import threading
# from PyQt5 import QtWidgets,QtCore
# import sys
# from time import sleep
# import pytest



# def test_btn_reinstall_grub(qtbot):
#     main.MainWindow=main.Ui()
#     mw=main.MainWindow
#     mw.tabWidget.setCurrentIndex(2) 

    
#     lv=mw.chroot.listWidget
#     item =lv.item(0)
#     rect = lv.visualItemRect(item)
#     center = rect.center()
#     print(center)
#     print(item.text())
#     assert lv.itemAt(center).text() == item.text()
#     # assert lv.currentRow() == 0

    
#     qtbot.mouseClick(mw.chroot.listWidget.viewport(),QtCore.Qt.LeftButton,pos=center)
#     # mw.chroot.listWidget.item(2).click()
#     assert type( mw.tabWidget.currentWidget()).__name__ =='ChrootAfterUi'
#     currentWidget=mw.tabWidget.currentWidget()
#     qtbot.mouseClick(currentWidget.btn_reinstall_grub_package,QtCore.Qt.LeftButton)
#     sleep(2)
    
