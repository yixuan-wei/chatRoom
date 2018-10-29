# chatRoom
based on python socket ----for experiment of Computer Network 2017<br>
created by: yixuan-wei & weiyue0307<br>
**requirements**: Python3, tkinter, PyQt5<br>
**GitHub**: https://github.com/yixuan-wei/chatRoom

> for mac, tkinter needs manual updates:
http://www.activestate.com/activetcl/downloads <br>
> version:8.5.18.0

socket format：
----
-|------------|--....

indicator|length|info

indicator: bit 0

		0: only one socket; 1: following socket exists; 2: close socket
		
length of info: bit 1-12

		info length in bytes

info: bit 13-4108(max): 

		--first one: destination%@%{senderName}%&%{message}; 
		--the following: {message}%$%

**TRUE SOURCE CODE**:
main.py 

Run:
----
**command**: py main.py<br>
**note**: start a server before any client is set up
