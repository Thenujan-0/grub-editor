#!/usr/bin/python3
import sys
import main
import os
import traceback
HOME =os.getenv('HOME')



import logging

logging.root.handlers = []

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f'{HOME}/.grub-editor/logs/main.log'),
        logging.StreamHandler()
    ]
)


def except_hook(cls,exception,traceback_):
	print('adasd asdasd')
	# sys.__excepthook__(cls, exception, traceback)
	print('exceas')
	# logging.error(traceback.format_exc())
	text = "".join(traceback.format_exception(exception))
	logging.error("Unhandled exception: %s", text)

def main_():
	main.main()


sys.excepthook = except_hook



if __name__ == '__main__':
	print('starting main')
	main_()

