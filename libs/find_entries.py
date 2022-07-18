"""This module is used to find the entries in the grub config file"""

import traceback
import subprocess


class GrubConfigNotFound(Exception):
    """ Raised when /boot/grub/grub.cfg is not found """


class MainEntry():
    parent=None
    title:str
    sub_entries=[]
    def __init__(self,title,sub_entries_):
        self.title = title
        self.sub_entries=sub_entries_
        
    def __repr__(self) -> str:
        to_return="" 
        if len(self.sub_entries)==0:
            return "MainEntry(title:'"+self.title+"')"
        
        for sub_entry in self.sub_entries:
            to_return+="\n"+sub_entry.title

        
        to_return="MainEntry(title:'"+self.title+"', sub_entries :["+to_return+"])"
            
        return to_return
        
    def set_parents_for_children(self):
        for child in self.sub_entries:
            child.parent=self     
        
        
    def echo(self):
        print('----------------------------------------------------------------')
        print('')
        print(self.title)
        
        print('printing sub_entries _____________')
        for sub_entry in self.sub_entries:
            print(sub_entry.title,'title of sub entry')
            print(sub_entry.parent,'parent of sub entry')
        print('finished printing for one big main entry')
        print('----------------')
        print('----------------')
        print('')
        
def find_entries():
    cmd_find_entries=["awk -F\\' '$1==\"menuentry \" || $1==\"submenu \" \
    {print i++ \" : \" $2}; /\\tmenuentry / {print \"\\t\" i-1\">\"j++ \" :\
        \" $2};' /boot/grub/grub.cfg"]
    
    out =subprocess.getoutput(cmd_find_entries)
    NO_SUCH_FILE_ERR_MSG="awk: fatal: cannot open file `/boot/grub/grub.cfg' for reading: No such file or directory"

    #if NO_SUCH_FILE_ERR_MSG in out:
    #raise GrubConfigNotFound
    
    main_entries=[]
    lines =out.splitlines()
    for line in lines:
        
        if line[0].isdigit():
            to_append=MainEntry(line[4:],[])
            main_entries.append(to_append)
            
        else:
            try:
                to_append=MainEntry(line[7:],[])
                main_entries[-1].sub_entries.append(to_append) 
            except IndexError as e:
                print(traceback.format_exc())
                print(e)
                print('error occured as an entry that was thought to be a sub entry couldnt be added to last main entry on the list .\
                    Error might have occured because the main_entries list is empty')
                print('--------------------------Printing the output of the command to find entries--------------------------------------')
                print(out)
                print("printing main entries",main_entries)
                print("printing to_append",to_append)
                print("line being parsed",line)



    for entry in main_entries:
        entry.set_parents_for_children()
        
    return main_entries
    
    
if __name__=="__main__":
    print(find_entries())
    