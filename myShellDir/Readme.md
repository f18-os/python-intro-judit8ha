
***- MY SHELL LAB-***

*-myShell executes with the following command './myShell-*

**SUPPORTED COMMANDS: -**

* single pipe 
* fork()
* Redirection 
* cd (cd .. , cd /some/path)
* It executes a command with direct path or not. 
* PS1 check for compatibility with testShell.py 


** please note that the following commands are working, however 
test shell shows as FAILED.

* cat /etc/passwd | sort 
* uname > /tmp/x
* cd .. 


**-BUGS -** 

Program CAN run and continue to bring up a shell, 
however this function has been intentionally disabled as 
the testShell causes it to go into an **infinite loop**. An idea might be 
that within this process I needed to implement a command to kill old 
running processes, unfortunately I was unable to implement this. 