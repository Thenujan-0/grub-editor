cmd_find_entries=["awk -F\\' '$1==\"menuentry \" || $1==\"submenu \" {print i++ \" : \" $2}; /\\tmenuentry / {print \"\\t\" i-1\">\"j++ \" : \" $2};' /boot/grub/grub.cfg"]
import traceback
import subprocess
out =subprocess.getoutput(cmd_find_entries)
class MainEntry():
    parent=None
    title:str
    sub_entries=[]
    def __init__(self,title,sub_entries_):
        self.title = title
        self.sub_entries=sub_entries_
        
    def set_parents_for_children(self):
        for child in self.sub_entries:
            child.parent=self     
        
        
    def echo(self):
        print('----------------------------------------------------------------')
        print('')
        print(self.title)
        
        print('printing sub_entries _____________')
        for i in range(len(self.sub_entries)):
            print(self.sub_entries[i].title,'title of sub entry')
            print(self.sub_entries[i].parent,'parent of sub entry')
        print('finished printing for one big main entry')
        print('----------------')
        print('----------------')
        print('')
main_entries=[]

lines =out.splitlines()
for i in range(len(lines)):
    
    if lines[i][0].isdigit():
        to_append=MainEntry(lines[i][4:],[])
        main_entries.append(to_append)
        
    else:
        try:
            to_append=MainEntry(lines[i][7:],[])
            main_entries[-1].sub_entries.append(to_append) 
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            print('error occured as an entry that was thought to be a sub entry couldnt be added to last main entry on the list .\
                  Error might have occured because the main_entries list is empty')
            print('--------------------------Printing the output of the command to find entries--------------------------------------')
            print(out)



for entry in main_entries:
    entry.set_parents_for_children()
    
    
if __name__=="__main__":
    print(main_entries)
    