#!/usr/bin/python3
import sys
import main
import os
import traceback
import logging
from math import floor

HOME =os.getenv('HOME')
if os.getenv("XDG_DATA_HOME") ==None:
    DATA_LOC=HOME+"/.local/share/grub-editor"
else:
    DATA_LOC=os.getenv("XDG_DATA_HOME")+"/grub-editor"
    
LOG_PATH=f'{DATA_LOC}/logs/main.log'

logging.root.handlers = []

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)


size= os.path.getsize(LOG_PATH)
if (size>5*10^6):
    with open(LOG_PATH) as f:
        data = f.read()
        ind=floor(len(data)/2)
        new_data =data[ind:]
    with open(LOG_PATH,"w") as f:
        f.write(new_data)
        
def except_hook(cls,exception,traceback_):
	# sys.__excepthook__(cls, exception, traceback)
	# logging.error(traceback.format_exc())
	text = "".join(traceback.format_exception(exception))
	logging.error("Unhandled exception: %s", text)

def main_():
	main.main()


sys.excepthook = except_hook



if __name__ == '__main__':
	print('starting main')
	main_()

