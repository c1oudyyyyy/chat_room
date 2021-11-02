import socket
import tkinter
import tkinter.messagebox
# import requests
import threading
import json
import tkinter.filedialog
from tkinter.scrolledtext import ScrolledText
import time

print("请不要关闭本窗口！")

IP = ''  # 用户ip
PORT = ''  # 用户端口
user = ''  # 用户名

local_test = ('127.0.0.1', 12345)  # 本地测试服务器的socket
server_socket = ('101.132.147.14', 12345)  # 阿里云服务器的socket

listbox1 = ''  # 用于显示在线用户的列表框
show = 1  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = '------Group chat-------'  # 群聊


# 登陆窗口
root0 = tkinter.Tk()
root0.geometry("350x150+600+300")
root0.title('welcome')
root0.resizable(0, 0)  # 禁止窗口缩放

IP0 = tkinter.StringVar()  # stringvar显示变量随时变更
IP0.set('101.132.147.14:12345')
USER = tkinter.StringVar()
USER.set('')

labelIP = tkinter.Label(root0, text='Group(socket)')
labelIP.place(x=20, y=20, width=100, height=40)
entryIP = tkinter.Entry(root0, width=60, textvariable=IP0)  # socket输入文本框
entryIP.place(x=120, y=25, width=150, height=30)

labelUSER = tkinter.Label(root0, text='user')
labelUSER.place(x=20, y=70, width=100, height=40)
entryUSER = tkinter.Entry(root0, width=60, textvariable=USER)  # user输入文本框
entryUSER.place(x=120, y=75, width=150, height=30)


def Login(*args):  # 登录。*args表示未知参数

    global IP, PORT, user
    IP, PORT = entryIP.get().split(':')  # 获取用户输入的socket
    user = entryUSER.get()
    if not user:
        tkinter.messagebox.showwarning('warning', message='用户名不能为空！')  # 警告弹窗
    else:
        root0.destroy()  # 登录成功，销毁该控件(登录窗口)


loginButton = tkinter.Button(
        root0, text="login", command=Login, activebackground='Gray')  # login按钮
loginButton.place(x=135, y=110, width=50, height=30)
root0.bind('<Return>', Login)  # 按下回车回调Login函数

root0.mainloop()  # 消息循环，刷新组件


# 建立连接
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 在客户端开启心跳维护
s.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 10000, 3000))
s.connect((IP, int(PORT)))  # 连接到服务器（请求报文包括客户端的ip和端口）
if user:
    s.send(user.encode())  # 发送用户名
else:
    s.send('用户名不存在'.encode())
    user = IP + ':' + PORT


# 聊天窗口
root1 = tkinter.Tk()
root1.geometry("600x500+450+100")
root1.title('聊天室')
root1.resizable(0, 0)  # 禁止缩放

listbox = ScrolledText(root1)  # 滚动消息界面
listbox.place(x=5, y=0, width=550, height=320)
listbox.tag_config('tag1', foreground='red', backgroun="yellow")
listbox.tag_config('tag2', foreground='red')
listbox.tag_config('tag3', foreground='blue')
listbox.tag_config('tag4', foreground='orange')
listbox.tag_config('tag5', foreground='green')
listbox.tag_config('tag6', foreground='pink')
listbox.tag_config('tag7', foreground='black', backgroun="yellow")

listbox.insert(tkinter.END, '欢迎进入群聊，开始聊天吧!'.rjust(29) + '\n', 'tag1')
listbox.insert(tkinter.END, time.ctime().rjust(40) + '\n', 'tag7')

INPUT = tkinter.StringVar()
INPUT.set('')
entryIuput = tkinter.Entry(root1, width=120, textvariable=INPUT)  # 聊天输入框
entryIuput.place(x=10, y=370, width=550, height=80)

# 在线用户列表
listbox1 = tkinter.Listbox(root1)
listbox1.place(x=445, y=0, width=130, height=320)


def send(*args):
    if chat not in users:
        tkinter.messagebox.showerror('error', message='无法连接至服务器!')
        return
    '''
    if chat == user:
        tkinter.messagebox.showerror('error', message='不能与自己聊天!')
        return
    '''
    message = entryIuput.get() +'~' + user + '~'+chat
    s.send(message.encode())
    INPUT.set('')


sendButton = tkinter.Button(root1, text="发送", command=send)
sendButton.place(x=520, y=453, width=40, height=25)
root1.bind('<Return>', send)


def receive():
    global uses
    while True:
        data = s.recv(1024)
        data = data.decode()
        # print(data)
        try:
            uses = json.loads(data)  # 收到在线用户信息
            listbox1.delete(0, tkinter.END)
            listbox1.insert(tkinter.END, "在线用户列表")
            listbox1.insert(tkinter.END, "------Group chat-------")
            for x in range(len(uses)):
                listbox1.insert(tkinter.END, uses[x])
            users.append('------Group chat-------')
        except:
            data = data.split('   `   ')  # 收到聊天信息
            message = data[0]
            userName = data[1]
            chatwith = data[2]
            message = '\n' + message
            if chatwith == '------Group chat-------':  # 群聊
                pos = message.find(':')
                messagel = message[0:pos]
                messager = message[pos:]
                if userName == user:
                    listbox.insert(tkinter.END, messagel, 'tag3')  # 末尾插入
                    listbox.insert(tkinter.END, messager)
                    listbox.insert(tkinter.END, '\t' + time.ctime(), 'tag5')
                else:
                    listbox.insert(tkinter.END, messagel, 'tag4')
                    listbox.insert(tkinter.END, messager)
                    listbox.insert(tkinter.END, '\t' + time.ctime(), 'tag5')
            elif userName == user or chatwith == user: # 私聊
                if userName == user:
                    listbox.tag_config('tag20', foreground='red')
                    listbox.insert(tkinter.END, message, 'tag20')
                else:
                    listbox.tag_config('tag30', foreground='green')
                    listbox.insert(tkinter.END, message,'tag30')

            listbox.see(tkinter.END)


r = threading.Thread(target=receive)
r.start()  # 开始线程接收信息

root1.mainloop()
s.close()  # 关闭聊天窗口后自动关闭远程连接

