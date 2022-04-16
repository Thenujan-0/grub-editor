from PyQt5 import QtWidgets,QtCore
import main
import subprocess
import os 
import sys
commented_config="""#GRUB_DEFAULT="Manjaro Linux"
#GRUB_TIMEOUT=20
#GRUB_TIMEOUT_STYLE=menu
#GRUB_DISTRIBUTOR="Manjaro"
#GRUB_CMDLINE_LINUX_DEFAULT="quiet apparmor=1 security=apparmor udev.log_priority=3"
#GRUB_CMDLINE_LINUX=""

# If you want to enable the save default function, uncomment the following
# line, and set GRUB_DEFAULT to saved.
GRUB_SAVEDEFAULT=true

# Preload both GPT and MBR modules so that they are not missed
GRUB_PRELOAD_MODULES="part_gpt part_msdos"



# Uncomment to ensure that the root filesystem is mounted read-only so that
# systemd-fsck can run the check automatically. We use 'fsck' by default, which
# needs 'rw' as boot parameter, to avoid delay in boot-time. 'fsck' needs to be
# removed from 'mkinitcpio.conf' to make 'systemd-fsck' work.
# See also Arch-Wiki: https://wiki.archlinux.org/index.php/Fsck#Boot_time_checking
#GRUB_ROOT_FS_RO=true

"""

PATH= os.path.dirname(os.path.realpath(__file__))
HOME=os.getenv('HOME')

def test_commented_lines(qtbot):
    tmp_file=f'{main.CACHE_LOC}/temp1.txt'
    subprocess.run([f'touch {tmp_file}'],shell=True)
    
    with open(tmp_file,'w') as f:
        f.write(commented_config)
    
    issues=[]
    val =main.get_value("GRUB_DEFAULT=",issues,tmp_file)
    assert val==None
    assert issues==[f"GRUB_DEFAULT= is commented out in {tmp_file}"]
    
    main.set_value("GRUB_DEFAULT=","Garuda Linux",tmp_file)
    
    
    issues=[]
    assert main.get_value("GRUB_DEFAULT=",issues,tmp_file)=="Garuda Linux"
    
        
config_fake_comment="""
GRUB_DEFAULT="Manjaro Linux"
GRUB_TIMEOUT=20
GRUB_TIMEOUT_STYLE=menu
GRUB_DISTRIBUTOR="Manjaro"
GRUB_CMDLINE_LINUX_DEFAULT="quiet apparmor=1 security=apparmor udev.log_priority=3"
GRUB_CMDLINE_LINUX=""
# setting 'GRUB_DEFAULT=saved'
"""

#after means that fake comment comes after the actual value
def test_fake_comment_after_get(qtbot):
    mw=main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)

    tmp_file=f'{main.CACHE_LOC}/temp2.txt'
    subprocess.run([f'touch {tmp_file}'],shell=True)
    
    with open(tmp_file,'w') as f:
        f.write(config_fake_comment)
    
    issues = []
    val = main.get_value("GRUB_DEFAULT=",issues,read_file=tmp_file)
    assert val == "Manjaro Linux"
    
    assert issues ==[]

#before means that fake comment comes before the actual value

config_fake_comment_before="""
#GRUB_DEFAULT=0
GRUB_DEFAULT="Manjaro Linux"
GRUB_TIMEOUT_STYLE=menu
GRUB_TIMEOUT=20
GRUB_DISTRIBUTOR="Manjaro"
GRUB_CMDLINE_LINUX_DEFAULT="quiet apparmor=1 security=apparmor udev.log_priority=3"
GRUB_CMDLINE_LINUX=""
# setting 'GRUB_DEFAULT=saved'
"""

def test_fake_comment_before_get(qtbot):
    mw=main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)
    
    tmp_file=f'{main.CACHE_LOC}/temp3.txt'
    subprocess.run([f'touch {tmp_file}'],shell=True)
    
    with open(tmp_file,'w') as f:
        f.write(config_fake_comment_before)
    
    issues=[]
    val =main.get_value("GRUB_DEFAULT=",issues,tmp_file)
    assert issues ==[]
    assert val == "Manjaro Linux"
    
    
config_last="""
GRUB_DEFAULT="Manjaro Linux"
GRUB_TIMEOUT=20
GRUB_TIMEOUT_STYLE=menu"""

def test_last_value(qtbot):
    mw=main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)
    
    tmp_file=f'{main.CACHE_LOC}/temp4.txt'
    subprocess.run([f'touch {tmp_file}'],shell=True)
    
    with open(tmp_file,'w') as f:
        f.write(config_last)
    
    issues=[]
    val =main.get_value("GRUB_TIMEOUT_STYLE=",issues,tmp_file)
    assert issues ==[]
    assert val=="menu"

def test_not_in_conf_val(qtbot):
    ''' Looking for a value that is not mentioned in the configuration '''
    mw=main.Ui()
    main.MainWindow=mw
    qtbot.addWidget(mw)
    
    tmp_file=f'{main.CACHE_LOC}/temp5.txt'
    subprocess.run([f'touch {tmp_file}'],shell=True)
    
    with open(tmp_file,'w') as f:
        f.write(config_last)
    issues=[]
        
    val =main.get_value("GRUB_CMDLINE_LINUX=",issues,tmp_file)
    assert issues ==[f"GRUB_CMDLINE_LINUX= was not found in {tmp_file}"]
    # todo exact issue
    assert val == None
    
    main.set_value("GRUB_CMDLINE_LINUX=","something fake",tmp_file)
    issues=[]
    new_val = main.get_value("GRUB_CMDLINE_LINUX=",issues,tmp_file)
    assert new_val =="something fake"
    assert issues==[]