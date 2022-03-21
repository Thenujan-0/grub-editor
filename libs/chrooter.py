import argparse
from time import sleep
import subprocess
import os 
import zmq
from  os_prober import get_os
import argparse
import threading
import sys
import logging
HOME =os.getenv('HOME')

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', 
                              '%m-%d-%Y %H:%M:%S')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler(f'{HOME}/chrooter.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


parser =argparse.ArgumentParser()
parser.add_argument('-p','--pid',help='pid of parent process')

args = parser.parse_args()
parent_pid =args.pid 


''' This is script is supposed to be executed with sudo permissions '''
print('pid of parent process is',parent_pid)

destination='/grub_editor_mount'


def start_chroot(partition,destination='/grub_editor_mount'):
    subprocess.run([f'mkdir -p {destination}'],shell=True)

    print(f"mount {partition} {destination}")
    logging.debug(subprocess.check_output([f"mount {partition} {destination}"],shell=True).decode())
    logging.debug(subprocess.check_output([f"mount --bind /sys {destination}/sys"],shell=True).decode())
    logging.debug(subprocess.check_output([f"mount --bind /proc {destination}/proc"],shell=True).decode())
    logging.debug(subprocess.check_output([f"mount --bind /dev {destination}/dev"],shell=True).decode())

    #cp /etc/resolv.conf to get internet connection inside chroot
    

def on_every_line(text):
    socket.send(bytes(text,'ascii'))
    
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")

def is_parent_running():
    try:
        os.kill(int(parent_pid),0)
        return True
    except OSError:
        return False

def die_when_parent_dies():
    while is_parent_running():
        sleep(2)
    os._exit(1)
    
threading.Thread(target=die_when_parent_dies).start()

def on_every_line(text):
    socket.send(bytes('partial '+text,'ascii'))
    socket.recv()



def reinstall_grub_package():
    
    resolv_path ='/etc/resolv.conf'

    if not  os.path.islink(resolv_path):
        logging.debug('etc/resolv.conf is not a symlink')
        subprocess.run([f'mount {resolv_path} {destination}/etc/resolv.conf --bind'],shell=True)
    else:
        subprocess.run([f'mount /run/NetworkManager/resolv.conf {destination}/etc/resolv.conf --bind'],shell=True)
    
    
    
    logging.info("gonna start reinstalling grub package")
    
    os_name=subprocess.check_output([f'chroot /grub_editor_mount /bin/bash -c "source /etc/os-release && echo \$NAME"'],shell=True).decode()
    arch_distros =["Manjaro Linux","EndeavourOS","Garuda Linux","ArcoLinux","RebornOS"]
    ubuntu_distros=["KDE neon","Ubuntu","Linux Mint","elementary OS","Zorin Os",'Pop!_OS']
    
    if os_name in arch_distros:
        p=subprocess.Popen([f'chroot /grub_editor_mount /bin/bash -c "pacman -S grub --no-confirm"'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True)
    elif os_name in ubuntu_distros:
        p=subprocess.Popen([f'chroot /grub_editor_mount /bin/bash -c "pacman -S grub --no-confirm"'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,shell=True)
        
    
    
    #used to determine if installation went successfully
    success=None
    
    for line in p.stdout:
        logging.info(line.decode()+'reading from stdout')
        if "resolving dependencies..." in line.decode():
            logging.info('emitted started signal chroot.py ')
            #todo use some message  to let the client know that it started successfully
            #else inform the user that it failed
            socket.send(b"started reinstalling successfully")
            success=True
            socket.recv()
        socket.send(bytes("reinstall_output "+line.decode()))
        socket.recv()
            
    # for line in p.stdout:
    #     sys.stdout.write(line.decode()+'reading from stdout')
    # if "resolving dependencies..." in line.decode():
    #     print('emitted started signal chroot.py ')
    if success:
        socket.send(b"finished reinstalling grub package")
    else:
        socket.send(b"reinstalling grub package failed")
        
    logging.info('reinstalling grub package finished')
# todo here




def umount(partition,destination='/grub_editor_mount'):
    logging.info(subprocess.check_output([f'umount {destination}/sys'],shell=True))
    logging.info(subprocess.check_output([f'umount {destination}/proc'],shell=True))
    logging.info(subprocess.check_output([f'umount {destination}/dev'],shell=True))
    logging.info(subprocess.check_output([f'umount {destination}'],shell=True))





while True:
    logging.info("server is running")
    message=socket.recv().decode()
    words = message.split()
    if words[0] =='get_os':
        print('client is asking for get_os')
        output=get_os(on_every_line)
        socket.send(bytes('final '+str(output),'ascii'))
    
    elif words[0] =='chroot':
        partition=words[1]
        start_chroot(partition)
        print('client has asked server to chroot')
        socket.send(b"started chroot")
    elif words[0]=='reinstall_grub_package':
        reinstall_grub_package()
    elif words[0] =='umount':
        umount(words[1])
    else:
        logging.info("recived unknown command")
        socket.send(b"unknown")
    print('server is running')
    logging.info("server is running")
    sleep(1)