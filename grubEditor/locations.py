import os

GRUB_CONF_LOC='/etc/default/grub'
file_loc=GRUB_CONF_LOC
HOME =os.getenv('HOME')

if os.getenv("XDG_CONFIG_HOME") is None:
    CONFIG_LOC=HOME+"/.config/grub-editor"
else:
    CONFIG_LOC=os.getenv("XDG_CONFIG_HOME")+"/grub-editor"
    
if os.getenv("XDG_CACHE_HOME") is None:
    CACHE_LOC=HOME+"/.cache/grub-editor"
else:
    CACHE_LOC=os.getenv("XDG_CACHE_HOME")+"/grub-editor"
    
if os.getenv("XDG_DATA_HOME") is None:
    DATA_LOC=HOME+"/.local/share/grub-editor"
else:
    DATA_LOC=os.getenv("XDG_DATA_HOME")+"/grub-editor"
    
    