[TOC]

# 一、实验目的

掌握Socket编程中流套接字的技术



# 二、实验内容

1. 掌握利用Socket进行编程的技术
2. 掌握多线程技术，保证双方可以同时发送
3. 建立聊天工具
4. 可以和多个人同时进行聊天
5. 使用图形界面，显示对方的语录



# 三、实验环境

服务器：Linux操作系统Ubuntu20.04（部署在阿里云ecs服务器）

客户端：windows操作系统（生成可执行文件，登录即可进入群聊）

编程语言：Python

编辑器：vscode、vim

主要技术：socket网络编程、多线程技术、Tkinter图形界面



# 四、主要思想

服务器运行后，创建新线程处理消息队列内的内容，即用于数据的转发。

客户端向服务器发送连接请求，服务器确认连接后就开启一个新的线程用于接收该客户端的数据，实现同时收发消息。

服务器可以同时与多个客户端建立连接，实现多人聊天。



# 五、关键技术

### Socket编程

- Server端

创建套接字：`s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)` AF_INET表示使用IPV4，SOCK_STREAM表示使用面向字节流的TCP协议

端口复用：`s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)` 这里是避免本地测试的时候重启服务器要等待一段时间才能重新使用指定的端口

绑定监听地址：`s.bind((IP, PORT))` 这里的IP为本地IP，Linux下可在terminal通过`ifconfig`查询

设置监听端口的排队等待数量：`s.listen(5)` 这里设置为5，表示在监听端口最多有5个连接请求在排队

阻塞式等待连接：`s.accept()` 返回一个连接对象`conn`和client端的socket，**与客户端的数据收发通过conn完成**

发送数据：`conn.send(data)` data必须编码为字节流

接收数据：`conn.recv()`



- Client端

创建套接字：与server相同

保活：避免一段时间没有数据传输时自动断开连接

```python
# 开启心跳维护，定期发送心跳包
s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
s.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 10000, 3000))
```

请求连接：`s.connect((IP, PORT))` 这里的IP是服务器的公网IP，PORT是服务器提供的端口号

发送数据：`s.send(data)` data必须编码为字节流

接收数据：`s.recv()` 



### 多线程技术

- 条件变量

创建：`con = threading.Condition()` 

获得一个锁：`con.acquire()`

释放一个锁：`con.release()`

令获得锁的线程进入等待池：`con.wait()` 进入等待池的线程会暂时释放锁

令等待池里的线程重新去争取一个锁：`con.notify()` 

- 条件变量解决的问题：

在生产者消费者模式下，消费者不会因为消息队列为空而陷入无限循环，导致cpu占满。

以下是本次实验所使用的条件变量

```python
    def Load(self, data, addr):
        con.acquire()  # 获得一个锁
        try:
            messages.put((addr, data))
            con.notify()  # 唤醒sendData所在的线程
            con.wait()  # 释放锁，进入等待池
        finally:
            con.release()  # 解锁

    def sendData(self):
        con.acquire()  # 获得一个锁
        while True:
            if not messages.empty():  # 消息队列不为空时
                message = messages.get()
                con.notify()  # 唤醒Load所在的线程
                if isinstance(message[1], str):
                    for i in range(len(users)):
                        data = message[1]
                        users[i][1].send(data.encode())
                        print(data)

                if isinstance(message[1], list):
                    data = json.dumps(message[1])
                    for i in range(len(users)):
                        try:
                            users[i][1].send(data.encode())
                        except:
                            pass
            else:
                con.wait()  # 消息队列为空，阻塞于此，等待其他线程的notify
        # con.release()
```
