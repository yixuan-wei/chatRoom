# coding:utf-8
# need manually update tkinter for chinese usage in mac OS

from threading import Thread
import socket
import select
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import platform  # for platform.platform
import os  # for os.system
import ast  # For ast.literal_eval()
import sys


# TODO 消息间上下距离减小 ???
# TODO 界面
# TODO 公共与私聊
# TODO 发送图片
# TODO 用户名'clientlist:'的解决

def data_encoder(data):
    rest = len(data)
    i = 0
    res = b''
    while True:

        if rest > 4096:
            res += '1'.encode() + '4096'.encode() + data[i:i + 4096]
            i += 4096
            rest -= 4096
        else:
            rest = str(rest)
            res += '0'.encode() + rest.zfill(12).encode() + data[i:]
            break
    return res


def get_nick(msg):
    return msg[msg.find('%@%') + 3: msg.find('%&%')]


def get_dest(msg):
    return msg[: msg.find('%@%')]


def restart_window(self):
    try:
        self.re_client.destroy()
    except:
        pass
    try:
        self.chat_frame.destroy()
        self.entry_frame.destroy()
        self.clients_frame.destroy()
        self.chat_entry.destroy()
        self.chat_text.destroy()
        self.send_button.destroy()
        # self.clist.destroy()
        self.group_chat.destroy()
        for r in self.clientlist:
            r.destroy()
        self.radio_label.destroy()
        self.frame.destroy()
    except:
        pass
    self.text = tk.Text(self, width=28, height=2, state=tk.NORMAL)
    self.text.insert(1.0, 'No server on such IP address\nOr connection failed')
    self.text.config(state=tk.DISABLED)
    self.text.pack()

    window.launch()


def rename(self):
    self.host_entry_label.destroy()
    self.host_entry.destroy()
    self.nick_entry_label.destroy()
    self.nick_entry.destroy()
    self.launch_button.destroy()
    self.frame.pack_forget()

    self.text1 = tk.Text(self, width=28, height=1, state=tk.NORMAL)
    self.text1.insert(1.0, 'repeated nick name!')
    self.text1.config(state=tk.DISABLED)
    self.text1.pack()

    window.client_menu()


def get_message_end(msg):
    msg = msg[3: -2]
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
        try:
            self.client_button.destroy()
            self.server_button.destroy()
        except:
            pass
        try:
            self.text.destroy()
        except:
            pass
        self.host_entry_label = ttk.Label(self.frame, text='Server Host Name/IP Address', anchor=tk.W, justify=tk.LEFT)
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
        try:
            self.text.destroy()
        except:
            pass
        self.title('Chat Room Server Log')
        # 获取本机ip
        myname = socket.gethostname()
        myaddr = socket.gethostbyname_ex(myname)[2]

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.settimeout(0.2)

        for addr in myaddr:
            try:
                self.server_socket.bind((addr, 8088))
                break
            except:
                continue
        self.host, self.port = self.server_socket.getsockname()
        if self.host == '':
            restart_window(self)

        self.log_frame = ttk.Frame(self)

        self.log_frame.style = ttk.Style()
        self.log_frame.style.theme_use(self.theme_use)

        msg = 'Server running at {0}:{1}.'.format(self.host, self.port)
        self.server_message = ttk.Label(self.frame, text=msg)
        self.server_log = tk.Text(self.log_frame, state=tk.DISABLED)

        self.server_log.pack(expand=True, fill=tk.BOTH)
        self.server_message.pack()
        self.log_frame.pack(expand=True, fill=tk.BOTH)

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

                firstbyte = '1'.encode()
                while firstbyte == b'1':
                    firstbyte = client.recv(1)
                    if firstbyte == b'':
                        print('nothing received from client in the first time')
                        break
                    length = client.recv(12)
                    data = client.recv(int(length.decode()))

                    nick = get_nick(data.decode())  # 已经是string格式

                if not self.client_sockets.__contains__(nick):
                    client.send(data_encoder('ACCEPT'.encode()))  #TODO 没发出去？
                    self.server_log.config(state=tk.NORMAL)
                    self.server_log.insert(tk.END, 'Nick {0} connected from {1}\n'.format(nick, addr))
                    self.server_log.config(state=tk.DISABLED)

                    self.clients[addr] = nick
                    self.client_sockets[nick] = client

                    for name in self.client_sockets:
                        self.client_sockets[name].send(data_encoder(
                            ('clientlist:' + str(list(self.client_sockets.keys()))).encode()))

                    t = Thread(name='client {0}'.format(nick), target=self.socket_comm, args=(addr,))
                    self.client_comm_threads.append(t)
                    t.start()

                else:
                    client.send(data_encoder('RENAME'.encode()))

            except socket.timeout:
                continue

    def socket_comm(self, addr):
        nick = self.clients[addr]

        csocket = self.client_sockets[nick]

        while not self.should_quit:
            r, _, _ = select.select([csocket], [], [])
            if r:
                firstbyte = '1'.encode()
                data = b''
                while firstbyte == b'1':
                    firstbyte = csocket.recv(1)
                    if firstbyte == b'':
                        break
                    length = csocket.recv(12)
                    data += csocket.recv(int(length.decode()))

                if len(data):

                    dest = get_dest(data.decode())
                    if dest==nick:  # TODO 不给自己发
                        continue

                    self.server_log.config(state=tk.NORMAL)
                    self.server_log.insert(tk.END, 'Sending msg from {0} \n'.format(nick))
                    self.server_log.config(state=tk.DISABLED)
                    if dest == 'Group Chat%%':
                        for name in self.client_sockets:
                            if name != nick:
                                self.client_sockets[name].send(data_encoder(data))
                    elif self.client_sockets.__contains__(dest):
                        self.server_log.config(state=tk.NORMAL)
                        self.server_log.insert(tk.END, 'Sending msg from {0} to {1}\n'.format(nick, dest))
                        self.server_log.config(state=tk.DISABLED)
                        self.client_sockets[dest].send(data_encoder(data))

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
            self.client_sockets[name].send(
                data_encoder(('clientlist:' + str(list(self.client_sockets.keys()))).encode()))

    def launch_client(self):
        self.host = self.host_entry.get()
        self.port = 8088
        self.nick = self.nick_entry.get()

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
        except:
            self.title('WARNING!')
            self.re_client = tk.Button(self, text='RETRY')
            self.re_client.bind('<Button-1>', restart_window(self))
            self.re_client.pack()

        try:
            self.text1.destroy()
        except:
            pass

        hello = '%@%{0}%&%Please allow connection!'.format(self.nick).encode()
        self.client_socket.send(data_encoder(hello))
        reaction = self.client_socket.recv(1024)[13:]
        print(reaction)

        if reaction.decode() == 'ACCEPT':
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

            self.chat_entry = scrolledtext.ScrolledText(self.entry_frame, height=3, wrap=tk.WORD)
            self.send_button = ttk.Button(self.entry_frame, text='Send')
            self.send_button.bind('<Button-1>', self.sending)
            self.chat_entry.bind('<Shift-Return>', self.sending)

            self.entry_frame.pack(side=tk.BOTTOM, fill=tk.X)
            self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.clients_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

            self.chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.send_button.pack(side=tk.RIGHT)

            self.clients = ast.literal_eval((self.client_socket.recv(1024)[24:]).decode())
            print(self.clients)
            self.dest = tk.StringVar()
            self.clientlist = []
            # self.clist = tk.Listbox(self.clients_frame,font=('Arial',15))

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

            self.group_chat = ttk.Radiobutton(self.clients_frame, text='Group Chat', variable=self.dest, value='Group Chat%%')
            self.group_chat.pack(anchor=tk.W)
            for client in self.clients:
                print('first send clientlist')
                # self.clist.insert(tk.END, client)
                r = ttk.Radiobutton(self.clients_frame, text=client, variable=self.dest, value=client)
                r.pack(anchor=tk.W)
                self.clientlist.append(r)

            # self.clist.pack(anchor=tk.W)

            self.dest.set(self.clients[0])

            self.chat_entry.focus_set()

            self.clientd_thread = Thread(name='clientd', target=self.clientd)
            self.clientd_thread.start()

        else:
            rename(self)

    def sending(self, event):

        message = self.chat_entry.get(1.0, tk.END)
        if message != '':
            dest = self.dest.get()
            data = '{0}%@%{1}%&%{2}%$%'.format(dest, self.nick, message)
            # 将sender放在前面，这样再和整体的数据连接之后，再进行分批处理，就会只有一个sender，就不会有多个sender了
            data = data.encode()
            # 在class外侧单独写一个编码函数data_encoder()，方便调用
            data = data_encoder(data)

            self.chat_entry.delete(1.0, tk.END)
            # Now we get the handled data, and we can send it
            self.client_socket.send(data)
            if dest == 'Group Chat%%':
                dest = 'all clients'

            self.chat_text.config(state=tk.NORMAL)
            self.chat_text.insert(tk.END, 'To {0}'.format(dest), ('tag{0}'.format(self.__i)))
            self.chat_text.insert(tk.END, ': {0}\n'.format(message), ('tag{0}'.format(self.__j)))
            self.chat_text.tag_config('tag{0}'.format(self.__i), justify=tk.RIGHT, foreground=color[color_hash('self')],
                                      font='Times 14 bold', underline=True)
            self.chat_text.tag_config('tag{0}'.format(self.__j), justify=tk.RIGHT, foreground='black')
            self.chat_text.config(state=tk.DISABLED)

            self.__i = self.__i + 2
            self.__j = self.__j + 2

            self.chat_text.see(tk.END)

    def clientd(self):
        while not self.should_quit:
            try:
                firstbyte = '1'.encode()
                senderflag = 1
                message = ""
                while firstbyte == '1'.encode():
                    firstbyte = self.client_socket.recv(1)
                    if firstbyte == b'':
                        break
                    if firstbyte == b'2':
                        print('server closed')
                        restart_window(self)
                        break
                    length = self.client_socket.recv(12)
                    data = self.client_socket.recv(int(length.decode()))

                    if data[: 11] == 'clientlist:'.encode():

                        self.clients = ast.literal_eval((data[11:]).decode())

                        for r in self.clientlist:
                            r.destroy()
                        # self.clist.delete(0, tk.END)
                        for client in self.clients:
                            r = ttk.Radiobutton(self.clients_frame, text=client, variable=self.dest, value=client)
                            r.pack(anchor=tk.W)
                            # self.clist.insert(tk.END, client)
                            self.clientlist.append(r)
                        # self.clist.pack(anchor=tk.W)
                    else:
                        if senderflag:
                            sender = get_nick(data.decode())  # 已经是string格式
                            senderflag = 0
                            if firstbyte == b'0':
                                message += get_message_end(data.decode())  # 已经是string格式
                            else:
                                message += get_message_unend(data.decode())  # 已经是string格式
                        else:
                            if firstbyte == b'0':
                                message += get_message_end(data.decode())  # 已经是string格式
                            else:
                                message += get_message_unend(data.decode())  # 已经是string格式

                # 此时的sender和message都已经为string格式
                self.chat_text.config(state=tk.NORMAL)
                self.chat_text.insert(tk.END, '{0}'.format(sender), ('tag{0}'.format(self.__i)))
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
        for nick in self.client_sockets:
            print('ready to close socket', nick)
            self.client_sockets[nick].send(b'2')
            self.client_sockets[nick].shutdown(socket.SHUT_WR)
            self.client_sockets[nick].close()
        self.server_socket.close()

        for t in self.client_comm_threads:
            print('ready to close', t)
            t.join(1)
        self.serverd_thread.join(1)

        self.destroy()

    def client_quit(self):
        self.should_quit = True
        self.client_socket.shutdown(socket.SHUT_WR)
        self.client_socket.close()
        self.clientd_thread.join(1)

        self.destroy()
        sys.exit()


if __name__ == '__main__':
    window = window()
    window.launch()
