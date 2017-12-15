#coding:utf-8

from threading import Thread
import socket
import select
import tkinter as tk
from tkinter import ttk
import platform  # for platform.platform
import os  # for os.system
import ast  #For ast.literal_eval()
import sys

# TODO server挂掉client的处理
# TODO socket.connect refused的错误处理
# TODO tk & ttk格式全错
# TODO send中str改byte :已在sending和cliented函数中修改，加入encode()和decode()


# TODO 改变头处理，配合信息格式254行，109，140
# TODO 数据编码处理函数data_encoder()
def data_encoder(data):
    rest = len(data)
    i = 0
    res = b''
    while True:
        restflag = rest / (1<<12)
        if restflag:
            res += bytes(1) + bytes(4096) + data[i:i+4095]
            i += 4096
            rest %= (1<<12)
        else:
            rest %= (1<<12)
            res += bytes(0) + bytes(rest.zfill(12)) + data[i:]
            break
    return res

def get_nick(msg):
    msg = msg[3:]
    return msg[: msg.find('%&%')]


def get_dest(msg):
    msg = msg[3:]
    return msg[: msg.find('%@%')]


def get_message_end(msg):
    msg = msg[3: -3]
    return msg[msg.find('%&%') + 3: msg.rfind('%$%')]

def get_message_unend(msg):
    msg = msg[3:]
    return msg[msg.find('%&%') + 3:]


color = ['red', 'blue', 'green', 'pink', 'yellow', 'grey', 'magenta', 'orange', 'purple', 'violet', 'indigo']

def color_hash(str):
    result = 0
    a = ord(str[0])
    for c in str[1:]:
        b = ord(c)
        result = result + a * b
        a = b

    return result % 10

class window(tk.Tk):

    def launch(self):
        self.title('chat room')
        self.frame = ttk.Frame(self)
        self.frame.style = ttk.Style()

        self.server_button = ttk.Button(self.frame, text='Launch Server', command=self.launch_server)
        self.client_button = ttk.Button(self.frame, text='Launch Client', command=self.client_menu)

        self.server_button.grid(row=0, column=0, columnspan=2, rowspan=2, padx=40, pady=30)
        self.client_button.grid(row=2, column=0, columnspan=2, rowspan=2, padx=40, pady=30)

        self.frame.pack(fill=tk.BOTH, expand=True)

        if platform.platform()[:6] == 'Darwin':
            self.theme_use = 'aqua'
            os.system("""/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true'""")

        else:
            self.theme_use = 'default'
            self.lift()

        self.frame.style.theme_use(self.theme_use)
        self.mainloop()

    def client_menu(self):
        self.client_button.destroy()
        self.server_button.destroy()

        self.host_entry_label = ttk.Label(self.frame, text='Server Host Name/IP Address', anchor=tk.W,justify=tk.LEFT)
        self.host_entry = ttk.Entry(self.frame)

        self.nick_entry_label = ttk.Label(self.frame, text='Nick Name', anchor=tk.W, justify=tk.LEFT)
        self.nick_entry = ttk.Entry(self.frame)

        self.launch_button = ttk.Button(self.frame, text='Launch as Client!', command=self.launch_client)

        self.host_entry_label.grid(row=0, column=0, pady=10, padx=5)
        self.host_entry.grid(row=0, column=1, pady=10, padx=5)
        self.nick_entry_label.grid(row=1, column=0, pady=10, padx=5)
        self.nick_entry.grid(row=1, column=1, pady=10, padx=5)
        self.launch_button.grid(row=2, column=0, columnspan=2, pady=10, padx=5)

        self.host_entry.focus_set()

    def launch_server(self):
        self.client_button.destroy()
        self.server_button.destroy()
        self.title('Chat Room Server Log')

        self.host = '127.0.0.1'
        self.port = '8088'
        self.log_frame = ttk.Frame(self)

        self.log_frame.style = ttk.Style()
        self.log_frame.style.theme_use(self.theme_use)

        msg = 'Server running at {0}:{1}.'.format(self.host, self.port)
        self.server_message = ttk.Label(self.frame, text=msg)
        self.server_log = tk.Text(self.log_frame, state=tk.DISABLED)

        self.server_log.pack(expand=True, fill=tk.BOTH)
        self.server_message.pack()
        self.log_frame.pack(expand=True, fill=tk.BOTH)

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.settimeout(0.2)
        self.server_socket.bind((self.host, self.port))

        self.client_sockets = {}  # Dictionary -> nick:socket
        self.clients = {}  # Dictionary -> address:nick_name

        self.serverd_thread = Thread(name='serverd', target=self.serverd)
        self.client_comm_threads = []

        self.serverd_thread.start()

    def serverd(self):
        self.server_socket.listen(5)
        self.should_quit = False
        self.protocol('WM_DELETE_WINDOW', self.server_quit)

        while not self.should_quit:
            try:
                client, addr = self.server_socket.accept()
                client.settimeout(1.0)

                #first_data = client.recv(1024)
                #  TODO head processing，配合17，140，254
                #nick = get_nick(first_data)
                firstbyte = bytes(1)
                senderflag = 1
                message = ""
                while firstbyte:
                    firstbyte = client.recv(1)
                    length = client.recv(12)
                    data = client.recv(length)
                    # TODO 消息格式
                    if senderflag :
                        nick = get_nick(data.decode()) #已经是string格式
                        senderflag = 0
                        if firstbyte == 0:
                            message += get_message_end(data.decode()) # 已经是string格式
                        else:
                            message += get_message_unend(data.decode()) # 已经是string格式
                    else:
                        if firstbyte == 0:
                            message += get_message_end(data.decode()) # 已经是string格式
                        else:
                            message += get_message_unend(data.decode()) # 已经是string格式

                self.server_log.config(state=tk.NORMAL)
                self.server_log.insert(tk.INSERT, 'Nick {0} connected from {1}\n'.format(nick, addr))
                self.server_log.config(state=tk.DISABLED)

                self.clients[addr] = nick
                self.client_sockets[nick] = client

                for name in self.client_sockets:
                    self.client_sockets[name].sending('clientlist:' + str(self.client_sockets.keys()))

                t = Thread(name='client {0}'.format(nick), target=self.socket_comm, args=(addr,))

                t.start()

            except socket.timeout:
                continue

    def socket_comm(self, addr):
        nick = self.clients[addr]

        csocket = self.client_sockets[nick]

        while not self.should_quit:
            r, _, _ = select.select([csocket], [], [])
            if r:
                data = csocket.recv(1024)

                if len(data):
                    # TODO 修改成聊天室模式，配合17，104，254行
                    dest = get_dest(data)
                    if self.client_sockets.has_key(dest):
                        self.server_log.config(state=tk.NORMAL)
                        self.server_log.insert(tk.END, 'Sending msg from {0} to {1}\n'.format(nick, dest))
                        self.server_log.config(state=tk.DISABLED)

                        self.client_sockets[dest].sending(data)

                    else:
                        self.server_log.config(state=tk.NORMAL)
                        self.server_log.insert(tk.END, 'Invalid destination nick {0}\n'.format(dest))
                        self.server_log.config(state=tk.DISABLED)

                else:
                    break
            else:
                continue

        self.server_log.config(state=tk.NORMAL)
        self.server_log.insert(tk.END, 'Connection from {0} at {1} dropped.\n'.format(nick, addr))
        self.server_log.config(state=tk.DISABLED)

        csocket.close()

        self.client_sockets.pop(nick)
        self.clients.pop(addr)

        for name in self.client_sockets:
            self.client_sockets[name].sending('clientlist:' + str(self.client_sockets.keys()))

    def launch_client(self):
        self.host = self.host_entry.get()
        self.port = 8088
        self.nick = self.nick_entry.get()

        self.host_entry_label.destroy()
        self.host_entry.destroy()
        self.nick_entry_label.destroy()
        self.nick_entry.destroy()
        self.launch_button.destroy()
        self.frame.pack_forget()

        self.title('Chat Room Client: {0}'.format(self.nick))

        self.should_quit = False

        self.protocol('WM_DELETE_WINDOW', self.client_quit)

        self.chat_frame = ttk.Frame(self.frame, borderwidth=5)
        self.clients_frame = ttk.Frame(self.frame)
        self.entry_frame = ttk.Frame(self)

        self.chat_frame.style = ttk.Style()
        self.chat_frame.style.theme_use(self.theme_use)
        self.clients_frame.style = ttk.Style()
        self.clients_frame.style.theme_use(self.theme_use)
        self.entry_frame.style = ttk.Style()
        self.entry_frame.style.theme_use(self.theme_use)

        self.chat_text = tk.Text(self.chat_frame, state=tk.DISABLED)

        self.chat_entry = ttk.Entry(self.entry_frame)
        self.send_button = ttk.Button(self.entry_frame, text='Send')
        # TODO 聊天框格式设置 & 支持滚动
        self.send_button.bind('<Button-1>', self.sending)
        self.chat_entry.bind('<Return>', self.sending)

        self.entry_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.clients_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.send_button.pack(side=tk.RIGHT)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.client_socket.connect((self.host, self.port))
        self.client_socket.send('Please allow connection!%&%{0}%&%'.format(self.nick))
        self.clients = ast.literal_eval(self.client_socket.recv(1024)[11:]) # TODO 检查【11：】的用法
        # TODO 改变客户端左侧边栏：无选择只展示
        self.dest = tk.StringVar()
        self.radios = []

        self.radio_label = ttk.Label(self.clients_frame,
                                     width=15,
                                     wraplength=125,
                                     anchor=tk.W,
                                     justify=tk.LEFT,
                                     text='connected clients:')

        self.radio_label.pack()
        self.chat_text.pack(fill=tk.BOTH, expand=True)

        self.__i = 0
        self.__j = 1

        for client in self.clients:
            r = ttk.Radiobutton(self.clients_frame, text=client, variable=self.dest, value=client)
            r.pack(anchor=tk.W)

            self.radios.append(r)

        self.dest.set(self.clients[0])

        self.chat_entry.focus_set()

        self.clientd_thread = Thread(name='clientd', target=self.clientd)

        self.clientd_thread.start()

    def sending(self, event):
        # TODO 改变信息格式，配合头处理17，104，140行
        message = self.chat_entry.get()
        dest = self.dest.get()
        #data = '%@%{0}%@%{1}%&%{2}%&%'.format(dest, message, self.nick)
        data = '%@%{0}%&%{1}%$%'.format(self.nick, message)
        # TODO 将sender放在前面，这样再和整体的数据连接之后，再进行分批处理，就会只有一个sender，就不会有多个sender了
        data = data.encode()# TODO 转成bytes之后调用编码函数
        # TODO 在class外侧单独写一个编码函数data_encoder()，方便调用
        data = data_encoder(data)

        self.chat_entry.delete(0, tk.END)
        # TODO ：Now we get the handled data, and we can send it
        self.client_socket.send(data)

        self.chat_text.config(state=tk.NORMAL)
        self.chat_text.insert(tk.END, 'To {0}'.format(dest, message), ('tag{0}'.format(self.__i)))
        self.chat_text.insert(tk.END, ': {0}\n'.format(message), ('tag{0}'.format(self.__j)))
        self.chat_text.tag_config('tag{0}'.format(self.__i), justify=tk.RIGHT, foreground=color[color_hash(dest)],
                                  font='Times 14 bold', underline=True)
        self.chat_text.tag_config('tag{0}'.format(self.__j), justify=tk.RIGHT, foreground='black')
        self.chat_text.config(state=tk.DISABLED)

        self.__i = self.__i + 2
        self.__j = self.__j + 2

        self.chat_text.see(tk.END)

    def clientd(self):
        while not self.should_quit:
            try:
                # TODO 头文件处理 配合17，104，140，254行
                firstbyte = bytes(1)
                senderflag = 1
                message = ""
                while firstbyte:
                    firstbyte = self.client_socket.recv(1)
                    length = self.client_socket.recv(12)
                    data = self.client_socket.recv(length)

                    # TODO？？？: 这里的 if data[: 11] == 'clientlist:'：需要更改，为单选聊天对象问题
                    if data[: 11] == 'clientlist:':
                        self.clients = ast.literal_eval(data[11:])

                        for r in self.radios:
                            r.destroy()
                        for client in self.clients:
                            r = ttk.Radiobutton(self.clients_frame, text=client, variable=self.dest, value=client)
                            r.pack(anchor=tk.W)

                            self.radios.append(r)
                    else:
                        # TODO 消息格式
                        if senderflag :
                            sender = get_nick(data.decode()) #已经是string格式
                            senderflag = 0
                            if firstbyte == 0:
                                message += get_message_end(data.decode()) # 已经是string格式
                            else:
                                message += get_message_unend(data.decode()) # 已经是string格式
                        else:
                            if firstbyte == 0:
                                message += get_message_end(data.decode()) # 已经是string格式
                            else:
                                message += get_message_unend(data.decode()) # 已经是string格式

                # TODO: 此时的sender和message都已经为string格式
                self.chat_text.config(state=tk.NORMAL)
                self.chat_text.insert(tk.END, 'From {0}'.format(sender), ('tag{0}'.format(self.__i)))
                self.chat_text.insert(tk.END, ': {0}\n'.format(message), ('tag{0}'.format(self.__j)))
                self.chat_text.tag_config('tag{0}'.format(self.__i), justify=tk.LEFT,
                                          foreground=color[color_hash(sender)], font='Times 14 bold',
                                          underline=True)
                self.chat_text.tag_config('tag{0}'.format(self.__j), justify=tk.LEFT, foreground='black')
                self.chat_text.config(state=tk.DISABLED)

                self.__i = self.__i + 2
                self.__j = self.__j + 2

                self.chat_text.see(tk.END)
            except:
                continue

    def server_quit(self):
        self.should_quit = True

        for t in self.client_comm_threads:
            t.join()
        self.serverd_thread.join()

        for nick in self.client_sockets:
            self.client_sockets[nick].close()
        self.server_socket.close()
        self.destroy()

    def client_quit(self):
        self.should_quit = True
        self.client_socket.shutdown(socket.SHUT_WR)

        self.clientd_thread.join()
        self.client_socket.close()
        self.destroy()

if __name__=='__main__':
    window = window()
    window.launch()