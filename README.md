# chatRoom
based on python socket ----for experiment of Computer Network 2017

created by: yixuan-wei & weiyue0307

* for mac, tkinter needs manual updates:
http://www.activestate.com/activetcl/downloads
version:8.5.18.0

socket format：
----
-|------------|--....

indicator|length|info

indicator: bit 0

		0: only one socket; 1: following socket exists; 2: close socket
		
length of info: bit 1-12

		info length in bytes

info: bit 13-5004(max): 

		--first one: %@%{senderName}%&%{message}%$%; 
		--the following: message

TRUE SORCE CODE:
main.py 

failed attempts:
---
client.py -- client

server.py -- server

common.py -- message processing for both client & server
