#coding:utf-8
import socket, sys
from common import recv_all
import threading

#class clientsock:
s = None
host = '127.0.0.1'
port=8088
# Need further modify!!!!! We are considering move the client to the 'main' function in the file'client'
# There is a infinite circle in the "Please enter your massage:". So we are considering that leave out the multiple-threads,
# instead we will run them in the VMWare and Host
def client(HOST, PORT):
    #Find users in one addr, when a valid user is found, break
    #So in this 'for', finally we will only get one user
    for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
        except OSError:
            s = None
            print('socket() failed')
            continue

        try:
            s.connect((HOST, PORT))
        except OSError:
            s.close()
            s = None
            print('connect failed')
            continue
        break
    if s is None:
        print('could not open socket')
        sys.exit(1)
    #when a user is connected successfully, create a new subThread
    s.send(b'1')
    print(s.recv(4096).decode())
    #input the new user'self.s nickName as record
    nickName = input('input your nickName:')
    s.send(nickName.encode())

def sendThreadFunc():
    while True:
        try:
            myword = input('Please enter your message: ')
            #s.send(myword.encode())
            # !!!Here I don't deal with the length, Need further dealment!!!
            # determine the message length (max 255 characters, i.e. 3 digits), pad with leading zeroes
            msg_length_in_str = str(len(bytes(myword,encoding='utf-8')))
            msg_length_in_str = msg_length_in_str.zfill(12)
            s.sendall(bytes(msg_length_in_str + myword,encoding='utf-8'))  # add the length at the beginning of the message
            #reply = recv_all(s, 3)
            #print('Server:', repr(reply))
            #s.close()'''
        except ConnectionAbortedError:
            print('Server close this connection!')
        except ConnectionResetError:
            print('Server is closed!')

def recvThreadFunc():
    while True:
        try:
            otherword = s.recv(4096)
            if otherword:
                print(otherword.decode())
            else:
                pass
        except ConnectionAbortedError:
            print('Server closed this connection!')
        except ConnectionResetError:
            print('Server is closed!')



client(host,port)
th1 = threading.Thread(target = sendThreadFunc())
th2 = threading.Thread(target = recvThreadFunc())
threads = [th1, th2]
for t in threads:
    t.setDaemon(True)
    t.start()
t.join()

#s出现了Nonetype