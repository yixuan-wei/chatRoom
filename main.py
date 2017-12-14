#coding:utf-8
from client import clientsock
from server import serversock
from threading import Thread
import tkinter as tk
from tkinter import ttk
import platform  # for platform.platform
import os  # for os.system

host = '127.0.0.1'
port=8088


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
        self.server = serversock()
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
        self.server.server(self.host,self.port)



if __name__=='__main__':
    '''sthread = Thread(target=server,args=(host,port))
    sthread.daemon = True
    sthread.start()
    client = clientsock()
    Thread(target=client.main,args=(host,port)).start()
    '''
    window = window()
    window.launch()