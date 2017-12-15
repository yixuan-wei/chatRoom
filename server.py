# coding:utf-8
import socket, sys, select
from common import recv_all
import threading


class serversock:
    host = '127.0.0.1'
    port = 8088
    # store all the users' nicknames
    mydict = dict()
    # All the users connected to the server
    mylist = list()

    #waitable 的read list，表示异步通信中可读socket对象的列表
    inputs = []
    #连接进入server的client的名称
    fd_name ={}
    ''' def subThreadIn(self, myconnection, conNumber):
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
                return'''

    def server(self, HOST, PORT):
        #创建并初始化server socket
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
        return s

    # 创建一个新的socket连接
    def newConnection(self,ss):
        client_conn,client_addr = ss.accept()  # 响应一个client的连接请求, 建立一个连接,可以用来传输数据
        try:
            # 向client端发送欢迎信息
            client_conn.send(b"welcome to chatroom,pls set up your nick name!")
            client_name = client_conn.recv(1024) #接收client发来的昵称,最大接收字符为1024
            self.inputs.append(client_conn)
            self.fd_name[client_conn] = client_name  # 将连接/连接名 加入键值对
            client_conn.send(("current members in chatroom are: %s" % self.fd_name.values()).encode())
            # 向所有连接发送新成员加入信息
            for other in self.fd_name.keys():
                if other != client_conn and other != ss:
                    other.send((self.fd_name[client_conn]+" joined the chatroom!").encode())
        except Exception as e:
            print(e)
            ''' # get the length of the message first
            msg_length = int(recv_all(connectiono, 12))
            # get the 'real' message with proper length
            message = recv_all(connectiono, msg_length)
            print('Client said: ', message)
            connectiono.sendall(bytes('Bye',encoding='utf8'))
            connectiono.close()'''

    def closeConnection(self):
        pass

    def tellOthers(self, exceptNum, whatToSay):
        print('executing tellOthers, len of mylist:'+str(len(self.mylist)))
        for c in self.mylist:
            if c.fileno() != exceptNum:
                print('trying tell ' + str(c.fileno()) + whatToSay)
                try:
                    c.send(whatToSay.encode())  # TODO: 对方没接收到？？
                except:
                    pass

    def run(self):
        ss = self.server(self.host,self.port)
        #ss = self.serverInit()
        self.inputs.append(ss)
        print("Server is running...")
        while True:
            #rlist:wait until ready for reading
            #wlist:wait until ready for writing
            #elist:wait for an "exceptional condition"
            # rlist,wlist,elist = select.select(inputs, [], inputs,100)   # 如果只是服务器开启,100s之内没有client连接,则也会超时关闭
            rlist,wlist,elist = select.select(self.inputs, [], [])
            #当没有可读fd时，表示server错误，退出服务器
            if not rlist:
                print("timeout...")
                ss.close()
                break
            for r in rlist:
                if r is ss: # server socket, 表示有新的client连接请求
                    self.newConnection(ss)
                else:  # 表示一个client连接上有数据到达服务器
                    disconnect = False
                    try:
                        data = r.recv(4096)
                        #  TODO error: can't concat str to bytes
                        data = (self.fd_name[r] + " : " + data.decode()).encode() #确定客户端昵称
                    except socket.error:
                        data = bytes(self.fd_name[r] + " leaved the room")
                        disconnect = True
                    else:
                        pass
                    if disconnect:
                        self.inputs.remove(r)
                        print(data)
                        for other in self.inputs:
                            if other in self.inputs:
                                if other !=ss and other != r:#不发生到服务器和已经断开的连接
                                    try:
                                        other.send(data)
                                    except Exception as e:
                                        print(e)
                                    else:
                                        pass
                        del self.fd_name[r]
                    else:
                        print(data) #在服务器显示client发送的数据
                        #向其他成员（连接）发送相同的信息
                        for other in self.inputs:
                            if other!=ss and other!=r:
                                try:
                                    other.send(data)
                                except Exception as e:
                                    print(e)

if __name__ == "__main__":
    print("hi")
    server = serversock()
    server.run()

