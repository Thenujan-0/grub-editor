import subprocess
import os 
import sys
from PyQt5 import QtWidgets,QtCore

PATH=os.path.dirname(os.path.realpath(__file__))
PARENT_PATH=str(Path(PATH).parent)


print(PARENT_PATH)
sys.path.append(PARENT_PATH)

from  grubEdior.main.main import get_value, set_value,remove_value
from tools import create_tmp_file,get_file_sum
from  grubEdior.main import main

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
    tmp_file=create_tmp_file(commented_config)
    issues=[]
    val =get_value("GRUB_DEFAULT=",issues,tmp_file)
    assert val is None
    assert issues==[f"GRUB_DEFAULT= is commented out in {tmp_file}"]
    
    #check that the file doesn't change when trying to remove an already commented
    #config
    old_sum=get_file_sum(tmp_file)
    remove_value("GRUB_DEFAULT=",tmp_file)
    new_sum=get_file_sum(tmp_file)
    assert old_sum == new_sum
    
    
    set_value("GRUB_DEFAULT=","Garuda Linux",tmp_file)
    
    
    issues=[]
    print(tmp_file)
    assert get_value("GRUB_DEFAULT=",issues,tmp_file)=='Garuda Linux'
    
    remove_value("GRUB_DEFAULT=",tmp_file)
    assert get_value("GRUB_DEFAULT=",issues,tmp_file) is None
    
        




config_last="""
GRUB_DEFAULT="Manjaro Linux"
GRUB_TIMEOUT=20
GRUB_TIMEOUT_STYLE=menu"""

def test_last_value(qtbot):
    
    tmp_file=f'{main.CACHE_LOC}/temp4.txt'
    subprocess.run([f'touch {tmp_file}'],shell=True)
    
    with open(tmp_file,'w') as f:
        f.write(config_last)
    
    issues=[]
    val =main.get_value("GRUB_TIMEOUT_STYLE=",issues,tmp_file)
    assert issues ==[]
    assert val=="menu"
    
    remove_value("GRUB_TIMEOUT_STYLE=",tmp_file)
    assert get_value("GRUB_TIMEOUT_STYLE=",issues,tmp_file) is None


    