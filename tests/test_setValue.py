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

# Uncomment to enable booting from LUKS encrypted devices
#GRUB_ENABLE_CRYPTODISK=y

# Uncomment to use basic console
GRUB_TERMINAL_INPUT=console

# Uncomment to disable graphical terminal
#GRUB_TERMINAL_OUTPUT=console

# The resolution used on graphical terminal
# note that you can use only modes which your graphic card supports via VBE
# you can see them in real GRUB with the command 'videoinfo'
GRUB_GFXMODE=auto

# Uncomment to allow the kernel use the same resolution used by grub
GRUB_GFXPAYLOAD_LINUX=keep

# Uncomment if you want GRUB to pass to the Linux kernel the old parameter
# format "root=/dev/xxx" instead of "root=/dev/disk/by-uuid/xxx"
#GRUB_DISABLE_LINUX_UUID=true

# Uncomment to disable generation of recovery mode menu entries
GRUB_DISABLE_RECOVERY=true

# Uncomment this option to enable os-prober execution in the grub-mkconfig command
GRUB_DISABLE_OS_PROBER=false

# Uncomment and set to the desired menu colors.  Used by normal and wallpaper
# modes only.  Entries specified as foreground/background.
GRUB_COLOR_NORMAL="light-gray/black"
GRUB_COLOR_HIGHLIGHT="green/black"

# Uncomment one of them for the gfx desired, a image background or a gfxtheme
#GRUB_BACKGROUND="/usr/share/grub/background.png"
GRUB_THEME="/usr/share/grub/themes/manjaro/theme.txt"

# Uncomment to get a beep at GRUB start
#GRUB_INIT_TUNE="480 440 1"

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
    tmp_file=f'{HOME}/.cache/grub-editor/temp.txt'
    subprocess.run([f'touch {tmp_file}'],shell=True)
    
    #todo
    with open(tmp_file,'w') as f:
        f.write(commented_config)
    
    issues=[]
    main.get_value("GRUB_DEFAULT=",issues,tmp_file)
    assert issues==[f"GRUB_DEFAULT= is commented out in {tmp_file}"]
    
    main.set_value("GRUB_DEFAULT=","Garuda Linux")
    
    
    issues=[]
    assert main.get_value("GRUB_DEFAULT=",issues,read_file=tmp_file)=="Garuda Linux"
    
        
        