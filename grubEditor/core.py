from enum import Enum
import os

from grubEditor.locations import CACHE_LOC



class GRUB_CONF(str, Enum):
    GRUB_TIMEOUT = "GRUB_TIMEOUT="
    GRUB_DISABLE_OS_PROBER = "GRUB_DISABLE_OS_PROBER="
    GRUB_DEFAULT = "GRUB_DEFAULT="
    GRUB_TIMEOUT_STYLE = "GRUB_TIMEOUT_STYLE="
    GRUB_RECORDFAIL_TIMEOUT = "GRUB_RECORDFAIL_TIMEOUT="
    GRUB_CMDLINE_LINUX = "GRUB_CMDLINE_LINUX="

def remove_quotes(value:str)->str:
        """ Removes double quotes or single quotes from the begining and the end
            Only if the exist in both places
        """
        if value[0]=='"' and value[-1]=='"':
            value=value[1:-1]
        elif value[0]=="'" and value[-1]=="'":
            value=value[1:-1]
        
        return value
    
class CONF_HANDLER():
    current_file :str = "/etc/default/grub"
    
    

    def get(self, name:GRUB_CONF,issues,read_file=None, remove_quotes_=False):
        """arguments are  the string to look for 
        and the list to append issues to
        Note: It does some minor edits to the value read from the file before 
        returning it if name==GRUB_DEFAULT
        1.if the value is not saved then check for double quotes, if it has 
            double quotes then it will be removed if not then (Missing ") will be added
        2.replace " >" with ">" to make sure it is found as invalid
        
        """
        
        if read_file is None:
            read_file=self.current_file
        
        #check if last character is = to avoid possible bugs
        if name[-1] != '=':
            raise ValueError("name passed for get_value doesnt contain = as last character")

        with open(read_file) as file:
            data =file.read()
            lines=data.splitlines()
            
            # found the name that is being looked for in  a commented line
            found_commented=False
            
            val= None
            for line in lines:
                sline=line.strip()
                if  sline.find(f"#{name}")==0:
                    found_commented=True
                    
                if sline.find("#")==0:
                    continue
                elif sline.find(name)==0:
                    start_index= line.find(name)+len(name)
                    
                    val=sline[start_index:]
                    
            #remove the double quotes in the end and the begining
            if name==GRUB_CONF.GRUB_DEFAULT and val is not None:
                if val.find(">")>0 and val.find(" >")==-1:
                    val =val.replace(">"," >")
                elif val.find(" >")>0:
                    #GRUB default is obviously invalid to make sure that other functions detect that its invalid lets just
                    val.replace(" >",">")
                    
                if val !="saved" :
                    if val[0]=="\"" and val[-1]=='"':
                        val=val[1:-1]
                    elif not val.replace(" >","").isdigit():
                        val+=" (Missing \")"
                    
            if val is None:
                comment_issue_string =f"{name} is commented out in {read_file}"
                
                if found_commented and comment_issue_string not in issues:
                    issues.append(comment_issue_string)
                else:
                    issues.append(f"{name} was not found in {read_file}")
            elif remove_quotes_:
                val = remove_quotes(val)
            if name=="GRUB_DISABLE_OS_PROBER=" and val is None:
                val="true"
            return val

    def remove(self, name:GRUB_CONF,target_file=f"{CACHE_LOC}/temp.txt"):
        """ Removes the value from the value """
        if name[-1] != '=':
            raise ValueError("name passed for set_value doesn't contain = as last character")
        
        with open(target_file) as f:
            data=f.read()
            
        lines=data.splitlines()
        
        for ind ,line in enumerate(lines):
            sline=line.strip()
            
            #no need to read the line if it starts with #
            if sline.find("#")==0:
                continue
            
            elif sline.find(name)==0:
                lines[ind]=""
        
        to_write_data=""
        
        for line in lines:
            to_write_data+=line+"\n" 
        
        with open(target_file,'w') as file:
            file.write(to_write_data)   

    def set(self, name,val,target_file=f'{CACHE_LOC}/temp.txt'):
        """ writes the changes to target_file(default:~/.cache/grub-editor/temp.txt). call initialize_temp_file before start writing to temp.txt
        call self.saveConfs or cp the file from cache to original to finalize the changes
        
        Note: It does some minor edits to the value passed if name==GRUB_DEFAULT
        1.add double quotes if necessary
        2.replace " >" with ">"
        """

        if name[-1] != '=':
            raise ValueError("name passed for set_value doesn't contain = as last character")
        
        # if name not in available_conf_keys:
        #     raise ValueError("name not in available_conf_keys :"+name)
        
        if name ==GRUB_CONF.GRUB_DEFAULT and val!="saved":
            if val[0]!='"' and val[-1]!='"':
                val='"'+val+'"'
            if " >" in val:
                val= val.replace(" >",">")
        
        
        with open(target_file) as f:
            data=f.read()
            
        lines=data.splitlines()
        old_val=None
        for ind ,line in enumerate(lines):
            sline=line.strip()
            
            #no need to read the line if it starts with #
            if sline.find("#")==0:
                continue
            
            elif sline.find(name)==0:
                start_index= line.find(name)+len(name)
                old_val=line[start_index:]
                if old_val!="":
                    new_line =line.replace(old_val,val)
                    lines[ind]=new_line
                else:
                    print("empty string")
                    lines[ind]=name+val

        to_write_data=""
        
        for line in lines:
            to_write_data+=line+"\n"
        
        #if line wasn't found
        if old_val is None:
            to_write_data+=name+val
            
        with open(target_file,'w') as file:
            file.write(to_write_data)
            
conf_handler = CONF_HANDLER()