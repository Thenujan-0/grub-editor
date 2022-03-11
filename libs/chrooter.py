import argparse
from time import sleep
import subprocess
import os 
import zmq
from  os_prober import get_os
import argparse
import threading

parser =argparse.ArgumentParser()
parser.add_argument('-p','--pid',help='pid of parent process')

args = parser.parse_args()
parent_pid =args.pid 


''' This is script is supposed to be executed with sudo permissions '''
print('pid of parent process is',parent_pid)

def start_chroot(partition,destination='/grub_editor_mount'):


    subprocess.run([f'mkdir -p {destination}'],shell=True)

    print(f"mount {partition} {destination}")
    subprocess.check_output([f"mount {partition} {destination}"],shell=True)
    subprocess.check_output([f"mount --bind /sys {destination}/sys"],shell=True)
    subprocess.check_output([f"mount --bind /proc {destination}/proc"],shell=True)
    subprocess.check_output([f"mount --bind /dev {destination}/dev"],shell=True)

    #cp /etc/resolv.conf to get internet connection inside chroot
    resolv_path ='/etc/resolv.conf'

    if not  os.path.islink(resolv_path):
        print('etc/resolv.conf is not a symlink')
        subprocess.run([f'mount {resolv_path} {destination}/etc/resolv.conf --bind'],shell=True)
    else:
        subprocess.run([f'mount /run/NetworkManager/resolv.conf {destination}/etc/resolv.conf --bind'],shell=True)

def on_every_line(text):
    socket.send(bytes(text,'ascii'))
    
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")
print('server running')

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
    pass

while True:
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
    else:
        socket.send(b"unknown")
    print('server is running')
    sleep(1)