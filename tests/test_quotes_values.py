import sys
import os
from tools import create_tmp_file,create_snapshot

HOME =os.getenv('HOME')
PATH=os.path.dirname(os.path.realpath(__file__))

#parent dir
PATH=PATH[0:-5]
sys.path.append(PATH)

import main

QUOTED_GRUB_TIMEOUT="""
GRUB_DEFAULT="Manjaro Linux"
GRUB_TIMEOUT="-1"
GRUB_TIMEOUT_STYLE=menu
GRUB_DISTRIBUTOR="Manjaro"
GRUB_CMDLINE_LINUX_DEFAULT="quiet apparmor=1 security=apparmor udev.log_priority=3"
GRUB_CMDLINE_LINUX=""
# """


def test_quoted_grub_timeout(qtbot):
    mw = main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)
    FILE_PATH = create_tmp_file(QUOTED_GRUB_TIMEOUT)
    main.file_loc = FILE_PATH
    mw.setUiElements()
    val = main.get_value("GRUB_TIMEOUT=",[])
    assert val == "\"-1\""
    assert not mw.checkBox_boot_default_entry_after.isChecked()