#! /usr/bin/python3
# -*- coding: UTF-8 -*-

import socket
import threading
import queue
import json  # json.dumps(some)打包   json.loads(some)解包
import time
# import os
# import os.path
# import sys


'''
聊天室主要思想：
客户端请求连接时发送socket和用户名给服务器，建立连接后即可聊天：本质上是先发给服务器，然后服务器再发给每个客户端，
服务器独自开启一个新的线程用于处理消息队列里的内容，具体为将客户端发来的信息存储并发送到每个客户端，
服务器每次接受一个客户端的连接请求就开启一个新的线程用于接收客户端的数据。

'''


IP = 'x.x.x.x'  # 服务器本地ip
# IP = '127.0.0.1'  # 本地测试
PORT = 12345  # 聊天室进程端口
messages = queue.Queue()  # 消息队列，存放(地址，信息)，发送到客户端
users = []   # 0:userName 1:connection
con = threading.Condition()  # 条件变量


def onlines():  # 返回当前在线人员的用户名列表，用于客户端显示
    online = []
    for i in range(len(users)):
        online.append(users[i][0])
    return online


class ChatServer(threading.Thread):  # 继承一个线程类
    global users, que, lock

    def __init__(self):
        threading.Thread.__init__(self)
        self.s = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)  # ipv4、面向字节流(TCP连接)
        self.s.setsockopt(socket.SOL_SOCKET,
                socket.SO_REUSEADDR, 1)  # 端口复用的关键点

        # os.chdir(sys.path[0])

    def receive(self, conn, addr):
        # 登录部分
        user = conn.recv(1024)  # 接收客户端输入的用户名
        user = user.decode()  # 解码
        if user == '用户名不存在':
            user = addr[0] + ':' + str(addr[1])
        print("*****************{}加入聊天室".format(user))
        tag = 1  # 后缀序号
        temp = user
        for i in range(len(users)):  # 重名则加上后缀1 2 3...
            if users[i][0] == user:
                tag = tag + 1
                user = temp + str(tag)
        users.append((user, conn))
        USERS = onlines()
        self.Load(USERS, addr)  # 放进消息队列

        # 聊天部分
        try:  # 用户正在聊天
            while True:
                message = conn.recv(1024)  # 接收客户端发来的消息（user：xxxxx）
                message = message.decode()  # 解码
                message = user + ':' + message
                self.Load(message, addr)
            conn.close()
        except:  # 用户断开连接
            j = 0
            for man in users:
                if man[0] == user:
                    users.pop(j)
                    print("*****************{}退出聊天室".format(man[0]))
                    break
                j += 1

            USERS = onlines()
            self.Load(USERS, addr)
            conn.close()  # 连接关闭

    def Load(self, data, addr):
        con.acquire()  # 上锁
        try:
            messages.put((addr, data))
            con.notify()
            con.wait()
        finally:
            con.release()  # 解锁

    def sendData(self):
        con.acquire()
        while True:
            if not messages.empty():  # 消息队列不为空时
                message = messages.get()
                con.notify()
                if isinstance(message[1], str):  # 发送聊天信息
                    for i in range(len(users)):  # 循环发送到每个客户端
                        data = message[1]
                        users[i][1].send(data.encode())  # 发送
                    a, b, c = data.split('   `   ')
                    print(a, '(' + time.ctime() + ')')

                if isinstance(message[1], list):  # 发送在线用户列表
                    data = json.dumps(message[1])  # 数据编码,将数据转换为json字符串
                    flag = True
                    for i in range(len(users)):
                        try:
                            users[i][1].send(data.encode())
                        except:
                            flag = False

                    if flag == True:
                        print("-----------------当前在线用户--------------------------")
                        for u in message[1]:
                            print(u, end=',')
                        print("\n-------------------------------------------------------")
            else:
                con.wait()
        # con.release()

    def run(self):  # 开始该线程
        self.s.bind((IP, PORT))
        self.s.listen(5)
        q = threading.Thread(target=self.sendData)  # 开新线程发送数据
        q.start()
        while True:  # 阻塞，直至有客户端申请连接（登录），客户端连接后立刻开新线程接收客户端的信息
            # 接受与客户端的连接。注意：返回的addr是(host, port)元组类型，conn为connect连接的简写，即返回一个新的连接
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.receive,
                    args=(conn, addr))  # 开新线程接收数据
            t.start()
        self.s.close()


if __name__ == '__main__':
    cserver = ChatServer()
    cserver.start()  # 启动线程类

