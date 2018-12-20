#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# CREATE DATE:2018/06/25
# AUTHOR: Liuzy
# 脚本作用：
## 1.将ftp提供下载的文件下载至本地
## 2.将本地需要备份的文件打包上传至ftp服务器的备份目录下
# 脚本使用说明：
## 1.此脚本基于python 3 与 Python 2，Windows 服务器需要提前安装Python解释器
## 2.使用需要根绝实际情况修改以下参数：
### 2.1 将 localhost 参数修改为运行脚本的服务器的 ip 地址
### 2.2 将 downloaddir 参数修改为下载文件存放的路径，路径最后要加 /，确保目录存在
### 2.3 根据实际需求修改备份文件列表 backupfilelist ，列表中包含服务器需要备份至 ftp 服务器的备份文件的全路径
### 2.3 根据实际情况修改 downloadinfo 与 backupinfo
### 2.4 执行脚本需要加参数，如果备份为 backup,如果下载为 download。


import shutil, os, datetime, zipfile, sys
from ftplib import FTP

# 运行脚本的服务器地址
localhost = "10.0.0.17"
# 下载文件存放路径，路径最后要加 /，确保目录存在
downloaddir = "D:/Data/test/"
# 服务器需要备份的文件列表
backupfilelist = ["D:/Software/3389modify.exe",
              "D:/Software/MySQL/源码包/mysql-5.6.40.tar.gz",
              "D:/Software/向日葵.rar"]
# 下载所需信息，包括ftp服务器地址、端口、下载ftp用户名、密码
downloadinfo = ["10.0.0.17", 21, "download", "P@ssw0rd"]
# 备份所需信息，包括ftp服务器地址、端口、备份ftp用户名、密码
backupinfo = ["10.0.0.17", 21, "backup", "P@ssw0rd"]

# 定义当前时间格式
nowtime = datetime.datetime.now().strftime("%Y%m%d")
# 定义备份文件存放文件夹的名称格式
backupdirname = localhost + '_' + nowtime + '_' + "backupfile"


class ftpserver:
    def __init__(self, host, port, username, password, localpath):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.localpath = localpath

    def connect(self):
        ftp = FTP()
        ftp.connect(self.host, self.port)
        ftp.login(self.username, self.password)
        return ftp

    def downloadfile(self):
        bufsiza =  1024
        ftp = ftpserver.connect(self)
        file = ftp.nlst()
        for f in file:
            fp = open(self.localpath + f , 'wb')
            print("开始下载文件 %s ... " % (f))
            ftp.retrbinary('RETR ' + f, fp.write, bufsiza)
            ftp.set_debuglevel(0)
            fp.close()
            print("成功下载文件 %s 至 %s" % (f, self.localpath))
        ftp.quit()

    def backupfile(self):
        bufsize = 1024
        # 尝试创建备份文件存放文件夹
        try:
            os.mkdir(backupdirname)
        except Exception as e:
            print("目录 %s 已存在" % backupdirname)
        # 拷贝备份文件至指定文件夹
        for i in backupfilelist:
            shutil.copy(i, backupdirname)
            print("拷贝文件 %s 至目录 %s" % (i, backupdirname))
        # 压缩备份文件夹
        filelist = []
        backupzipname = backupdirname+'.tar'
        if os.path.isfile(backupdirname):
            filelist.append(backupdirname)
        else:
            for root,dirs,files in os.walk(backupdirname):
                for name in files:
                    filelist.append(os.path.join(root,name))
        zf = zipfile.ZipFile(backupzipname,"w",zipfile.ZIP_DEFLATED,allowZip64=True)
        for tar in filelist:
            arcname = tar[len(backupdirname):]
            zf.write(tar,arcname)
        zf.close()
        # 连接ftp服务器，备份文件
        ftp = ftpserver.connect(self)
        try:
            ftp.mkd(localhost)
        except Exception as e:
            print("目录 %s 已存在" % localhost )
        fp = open(backupzipname, 'rb')
        print("开始备份文件 %s ... " % backupzipname)
        ftp.storbinary('STOR ' + localhost + '/' +  backupzipname, fp, bufsize)
        ftp.set_debuglevel(0)
        fp.close()
        print("成功备份文件 %s 至服务端 %s" % (backupzipname, localhost + '/' + backupzipname))
        ftp.quit()
        # 删除存放备份文件的临时文件夹与压缩包
        try:
            os.unlink(backupzipname)
            shutil.rmtree(backupdirname)

        except Exception as e:
            print(e)



if sys.argv[1] == "download":
    download = ftpserver(downloadinfo[0], downloadinfo[1], downloadinfo[2], downloadinfo[3], downloaddir)
    download.downloadfile()
elif sys.argv[1] == "backup":
    backup = ftpserver(backupinfo[0], backupinfo[1], backupinfo[2], backupinfo[3], "")
    backup.backupfile()