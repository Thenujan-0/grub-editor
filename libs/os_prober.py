import subprocess
from time import sleep
import re
from tracemalloc import start

# output=subprocess.check_output(['pkexec os-prober'],shell=True).decode()
# print(output)

def getOs(onEveryLineSignal=None):
    """
    onEveryLineSignal:a pyqt signal that will be emitted on everyline of stdout
    returns list:operating_systems list:partitions 
    """

    # with open('os-prober.txt','r') as f:
    #     output = f.read()
    
    operating_systems=[]
    partitions=[]
    
    output = subprocess.Popen(['pkexec os-prober'],shell=True,stdout =subprocess.PIPE,stderr=subprocess.STDOUT)
    for line_ in output.stdout:
        
        line=line_.decode()
        
        #emit a signal if it was passed
        if  onEveryLineSignal:
            onEveryLineSignal.emit(line)
        
        print('reading from stdout',line)
        if "rmdir: failed to remove '/var/lib/os-prober/mount': Device or resource busy" in line:
            print('found error')
            return None,None
    # print(output)
        first_part_re =r"/dev/sd[a-z]\d+"
        matches =re.search(first_part_re,line)
        if matches is not None:
            # print(matches.group(0))


            start_index = line.index(':')+1
            partitions.append(matches.group(0))
            # print(line[start_index:])
            end_index=line[start_index:].index(':')+start_index
            # print(line[start_index])
            # print(line[end_index+start_index+1])
            # print(line[start_index:end_index])
            operating_systems.append(line[start_index:end_index])

    
        
    return operating_systems,partitions
        
        
