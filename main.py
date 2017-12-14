#coding:utf-8
from client import clientsock
from server import server
from threading import Thread

host = '127.0.0.1'
port=8088
if __name__=='__main__':
    sthread = Thread(target=server,args=(host,port))
    sthread.daemon = True
    sthread.start()
    client = clientsock()
    Thread(target=client.main,args=(host,port)).start()