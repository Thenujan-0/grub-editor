import argparse
from time import sleep
import subprocess
import os 
import elevate
parser =argparse.ArgumentParser("mounts and chroots a linux distro")

parser.add_argument("partition",help="partition to mount")
parser.add_argument("destination",help="destination to mount the partition",nargs='?',default="/grub_editor_mounts")


user = os.getenv('USER')
if user !='root':
    print('you are not root')
    print('current user is ',user)
    elevate.elevate()

args=parser.parse_args()

partition=args.partition
destination=args.destination

subprocess.run(['mkdir -p {destination}'],shell=True)

print(f"mount {partition} {destination}")
subprocess.check_output([f"mount {partition} {destination}"],shell=True)
subprocess.check_output([f"mount --bind /sys {destination}/sys"],shell=True)
subprocess.check_output([f"mount --bind /proc {destination}/proc"],shell=True)
subprocess.check_output([f"mount --bind /dev {destination}/dev"],shell=True)



# subprocess.run(['umount -a'],shell=True)
