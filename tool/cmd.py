from socket import *
import struct
import json
import os
import sys
import time
import dq
import time


def 重置指令(num: str):
    global cm
    cm = num


def mai(prot, FILEPATH):
    # 创建客户端
    client = socket(AF_INET, SOCK_STREAM)
    ip_port = ('192.168.10.11', prot)
    buffSize = 1024
    client.connect(ip_port)
    print("connecting...")

    # 开始通信
    while True:
        time.sleep(0.1)
        completed = client.recv(buffSize).decode("utf-8")
        print("用户的选择是：", end='')
        print(completed)
        print()
        # 用户选择要进行的服务，将选择发送给服务器
        # select = input(
        #     "请输入要选择的服务： 1--上传文件   2--下载文件  0--退出系统 3---启动全部 4---启动调试框 5---停止 6---休眠 7---唤醒 8---预览 9---日志 \n")
        # client.send(bytes(select, "utf-8"))

        # 上传文件
        if completed == "1":
            #             fileName = input("请输入要上传的文件名加后缀：").strip()
            fileName = "js.zip"
            fileInfor = FILEPATH + fileName

            # 得到文件的大小
            filesize_bytes = os.path.getsize(fileInfor)

            # 创建复制文件
            fileName = "new" + fileName

            # 创建字典用于报头
            dirc = {"fileName": fileName,
                    "fileSize": filesize_bytes}

            # 将字典转为JSON字符，再将字符串的长度打包
            head_infor = json.dumps(dirc)
            head_infor_len = struct.pack('i', len(head_infor))

            # 先发送报头长度，然后发送报头内容
            client.send(head_infor_len)
            client.send(head_infor.encode("utf-8"))

            # 发送真实文件
            with open(fileInfor, 'rb') as f:
                data = f.read()
                client.sendall(data)
                f.close()

            # 服务器若接受完文件会发送信号，客户端接收
            completed = client.recv(buffSize).decode("utf-8")
            if completed == "1":
                print("上传成功")
        # 下载文件
        elif completed == "2":
            # 用户输入文件信息，发送给服务器
            #             fileName = input("请输入要下载的文件名加后缀：").strip()
            fileName = "debug.zip"
            client.send(bytes(fileName, "utf-8"))
            # 默认文件存在，接受并解析报头的长度，接受报头的内容
            head_struct = client.recv(4)
            head_len = struct.unpack('i', head_struct)[0]
            data = client.recv(head_len)

            # 解析报头字典
            head_dir = json.loads(data.decode('utf-8'))
            filesize_b = head_dir["fileSize"]
            filename = head_dir["fileName"]

            # 接受真实的文件内容
            recv_len = 0
            recv_mesg = b''

            f = open("%s%s" % (FILEPATH, filename), "wb")

            while recv_len < filesize_b:
                if filesize_b - recv_len > buffSize:
                    # 假设未上传的文件数据大于最大传输数据
                    recv_mesg = client.recv(buffSize)
                    f.write(recv_mesg)
                    recv_len += len(recv_mesg)
                else:
                    # 需要传输的文件数据小于最大传输数据大小
                    recv_mesg = client.recv(filesize_b - recv_len)
                    recv_len += len(recv_mesg)
                    f.write(recv_mesg)
                    f.close()
                    print("文件接收完毕！")

            # 向服务器发送信号，文件已经上传完毕
            completed = "1"
            client.send(bytes(completed, "utf-8"))
        elif completed == "3":
            # 用户输入文件信息，发送给服务器
            #             fileName = input("请输入要下载的文件名加后缀：").strip()
            fileName = "debug.zip"
            client.send(bytes(fileName, "utf-8"))
            # 默认文件存在，接受并解析报头的长度，接受报头的内容
            head_struct = client.recv(4)
            head_len = struct.unpack('i', head_struct)[0]
            data = client.recv(head_len)

            # 解析报头字典
            head_dir = json.loads(data.decode('utf-8'))
            filesize_b = head_dir["fileSize"]
            filename = head_dir["fileName"]

            # 接受真实的文件内容
            recv_len = 0
            recv_mesg = b''

            f = open("%s%s" % (FILEPATH, filename), "wb")

            while recv_len < filesize_b:
                if filesize_b - recv_len > buffSize:
                    # 假设未上传的文件数据大于最大传输数据
                    recv_mesg = client.recv(buffSize)
                    f.write(recv_mesg)
                    recv_len += len(recv_mesg)
                else:
                    # 需要传输的文件数据小于最大传输数据大小
                    recv_mesg = client.recv(filesize_b - recv_len)
                    recv_len += len(recv_mesg)
                    f.write(recv_mesg)
                    f.close()
                    print("文件接收完毕！")

            # 向服务器发送信号，文件已经上传完毕
            completed = "1"
            client.send(bytes(completed, "utf-8"))
            重置指令("3")
            print("3")

        elif completed == "4":
            print("1")
        elif completed == "5":

            重置指令("5")
        elif completed == "6":
            print("1")
        elif completed == "7":
            print("1")
        elif completed == "8":
            print("1")
        elif completed == "9":

            if str(dq.log) != "0":
                client.send(bytes(str(dq.log), "utf-8"))
            else:
                client.send(bytes(str("no"), "utf-8"))
            dq.xr(0)
        # 退出客户端
        else:
            print("退出系统！")
            client.close()
            break


