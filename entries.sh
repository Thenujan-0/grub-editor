gawk  'BEGIN {                                                                                                                       
  l=0                                                                                                                                
  menuindex= 0                                                                                                                       
  stack[t=0] = 0                                                                                                                     
}                                                                                                                                    

function push(x) { stack[t++] = x }                                                                                                  

function pop() { if (t > 0) { return stack[--t] } else { return "" }  }                                                              

{                                                                                                                                    

if( $0 ~ /.*menu.*{.*/ )                                                                                                             
{                                                                                                                                    
  push( $0 )                                                                                                                         
  l++;                                                                                                                               

} else if( $0 ~ /.*{.*/ )                                                                                                            
{                                                                                                                                    
  push( $0 )                                                                                                                         

} else if( $0 ~ /.*}.*/ )                                                                                                            
{                                                                                                                                    
  X = pop()                                                                                                                          
  if( X ~ /.*menu.*{.*/ )                                                                                                            
  {                                                                                                                                  
     l--;                                                                                                                            
     match( X, /^[^'\'']*'\''([^'\'']*)'\''.*$/, arr )                                                                               

     if( l == 0 )                                                                                                                    
     {                                                                                                                               
       print menuindex ": " arr[1]                                                                                                   
       menuindex++                                                                                                                   
       submenu=0                                                                                                                     
     } else                                                                                                                          
     {                                                                                                                               
       print "  " (menuindex-1) ">" submenu " " arr[1]                                                                               
       submenu++                                                                                                                     
     }                                                                                                                               
  }                                                                                                                                  
}                                                                                                                                    

}' /boot/grub/grub.cfg