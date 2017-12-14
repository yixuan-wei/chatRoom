# coding:utf-8
import socket, sys
from common import recv_all
import threading


class serversock():
    # store all the users' nicknames
    mydict = dict()
    # All the users connected to the server
    mylist = list()

    def subThreadIn(self, myconnection, conNumber):
        nickname = myconnection.recv(4096).decode()
        self.mydict[myconnection.fileno()] = nickname
        self.mylist.append(myconnection)
        print(str(conNumber)+' has the nickname: '+nickname)
        self.tellOthers(conNumber, '[系统提示：' + self.mydict[conNumber] + '进入聊天室')
        while True:
            try:
                recedMsg = myconnection.recv(4096).decode()
                if recedMsg:
                    print(self.mydict[conNumber], ':', recedMsg)
                    self.tellOthers(conNumber, self.mydict[conNumber] + ' :' + recedMsg)
            except(OSError, ConnectionResetError):
                # one user left the chat room
                try:
                    self.mylist.remove(myconnection)
                except:
                    pass
                print(self.mydict[conNumber], 'exit', len(self.mylist), 'person left')
                self.tellOthers(conNumber, '[系统提示：' + self.mydict[conNumber] + '离开聊天室')
                myconnection.close()
                return

    def server(self, HOST, PORT):
        s = None
        for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
            af, socktype, proto, canonname, sa = res
            try:
                s = socket.socket(af, socktype, proto)
            except OSError:
                s = None
                print('socket() failed')
                continue
                # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(sa)
                s.listen(5)
            except OSError:
                s.close()
                s = None
                continue
            break
        if s is None:
            print('could not open socket')
            sys.exit(1)
        while True:
            print('Listening at', s.getsockname())
            sc, sockname = s.accept()  # wait here until there is a request
            print('Accept a new connection', sc.getsockname(), sc.fileno())
            try:
                # sc.settimeout(5)
                buf = sc.recv(4096).decode()
                print('receive '+buf)
                # when a new user come in, create a new thread
                if buf == '1':
                    sc.send(b'welcome to server!')
                    mythread = threading.Thread(target=self.subThreadIn, args=(sc, sc.fileno()))
                    mythread.setDaemon(True)
                    mythread.start()
                else:
                    sc.send(b'please go out!')
                    sc.close()
            except:
                pass
            ''' # get the length of the message first
            msg_length = int(recv_all(sc, 12))
            # get the 'real' message with proper length
            message = recv_all(sc, msg_length)
            print('Client said: ', message)
            sc.sendall(bytes('Bye',encoding='utf8'))
            sc.close()'''

    def tellOthers(self, exceptNum, whatToSay):
        print('executing tellOthers, len of mylist:'+str(len(self.mylist)))
        for c in self.mylist:
            if c.fileno() != exceptNum:
                print('trying tell ' + str(c.fileno()) + whatToSay)
                try:
                    c.send(whatToSay.encode())  # TODO: 对方没接收到？？
                except:
                    pass


if __name__ == "__main__":
    host = '127.0.0.1'
    port = 8088
    print("hi")
    server = serversock()
    server.server(host, port)
