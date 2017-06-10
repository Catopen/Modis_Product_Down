# -*- coding: utf-8 -*-

import os,shutil,zipfile
from Tkinter import *
import tkFileDialog
import threading
import ttk
import re
import sys
import time
import socket
import ftplib
import string

#MODIS FTP 地址
hostaddr = '198.118.194.40' # ftp地址
username = 'anonymous' # 用户名
password = 'user@' # 密码
port  =  21   # 端口号
modpath = 'allData/5/'
modisimgnamepart=[]
#构建ftp类
class myftp:
    def __init__(self, hostaddr, username, password, remotedir, port=21):
        self.hostaddr = hostaddr
        self.username = username
        self.password = password
        self.remotedir  = remotedir
        self.port     = port
        self.ftp      = ftplib.FTP()
        self.file_list = []
    def __del__(self):
        self.ftp.close()

    def cwdbak(self):
        try:
            while(len(self.ftp.pwd())>1):
                self.ftp.cwd('..')
            print u'切换到根目录成功!'
        except(Exception):
            print u'切换到根目录失败！'

    def login(self):
        ftp=self.ftp
        print 'start login'
        try:
            timeout=500
            socket.setdefaulttimeout(timeout)
            ftp.set_pasv(1)
            print u'开始连接到 %s' %(self.hostaddr)
            ftp.connect(self.hostaddr,self.port)
            print u' 成功连接到 %s' %(self.hostaddr)
            print u' 开始登陆到 %s' %(self.hostaddr)
            ftp.login(self.username,self.password)
            print u'成功登陆到 %s' %(self.hostaddr)
            debug_print(ftp.getwelcome())
        except Exception:
            print u'连接或登陆失败'
        if self.remotedir!=[]:            
            try:
                ftp.cwd(self.remotedir)
            except(Exception):
                print u'登陆到指定目录失败'
    def pwdbak(self):
        return self.ftp.pwd()
    def downloadfile(self, localfile, remotefile):
        file_handler = open(localfile, 'wb')
        self.ftp.retrbinary('RETR %s'%(remotefile), file_handler.write)
        file_handler.close()
    def getfiledir(self,remote):
        file_dirlist=[]
        self.ftp.cwd(remote)
        self.ftp.dir(None,file_dirlist.append)
        return file_dirlist
    def getfilenamelist(self,f_list):
        fsult_p=[]
        result=[]
        for f_file in f_list:
            temp=','.join(f_file.split())
            fsult_p=temp.split(',')
            if int(fsult_p[4])!=0:
                if fsult_p[8].split('.')[2] in modisimgnamepart:
                    result.append(fsult_p[8])
        return result


def selectOutPath():
    path_ = tkFileDialog.askdirectory()
    outputPath.set(path_)

def downprd():
    rownum = inputrownum.get()
    colnum = inputcolnum.get()
    prddown = inputprddown.get()
    prdtype = inputprdtype.get()
    prddatey = inputprddatey.get()
    prddatedbeg = inputprddatedbeg.get()
    prddatedend = inputprddatedend.get()
    outPath = outputPath.get()
    
    #确定行列号
    for row in rownum.split(','):
        for col in colnum.split(','):
            modisimgnamepart.append('h'+row+'v'+col)
    rootdir_remote =[]
    f = myftp(hostaddr, username, password, rootdir_remote, port)
    f.login()
    for i in range(int(prddatedbeg),int(prddatedend)):
        ii=i
        if ii<10:
            ii="00"+str(ii)
        elif ii>=10 and ii<100:
            ii="0"+str(ii)
        url=modpath+prdtype+'/'+str(prddatey)+'/'+str(ii)
        print u'The pwd path is',url
        try:
            namelist=f.getfilenamelist(f.getfiledir(url))
            print 'namelist is',namelist
            for j in namelist:
                f.downloadfile(outPath+'/'+j,j)
                prdlist.insert(END,j)
                print "download  success"
            f.cwdbak()
        except(Exception):
            continue
            print "The path %s is not exist!" %url

def thread_it(func, *args):
    t = threading.Thread(target=func, args=args)
    t.setDaemon(True)
    t.start()

if __name__ == '__main__':
    
    root = Tk()
    root.minsize(500,380)
    root.title("MODIS数据下载器")
    
    outputPath = StringVar()
    inputrownum = StringVar()
    inputcolnum = StringVar()
    inputprddown = StringVar() #已下载数据
    inputprdtype = StringVar() #产品类型
    ptype1 = 'MOD'
    ptype2 = 'MYD'
    ptype3 = 'MYD'
    inputprddatey = IntVar() #产品年份
    inputprddatedbeg = IntVar() #起始年积日
    inputprddatedend = IntVar() #终止年积日
    
    
    
    # 输入行列号
    Label(root,text = r"输入行号:").grid(row = 0,column =0, sticky = W)
    Entry(root, textvariable = inputrownum,width = 20).grid(row = 0, column = 1, sticky = W)
    Label(root,text = r"输入列号:").grid(row = 0,column =2, sticky = E)
    Entry(root, textvariable = inputcolnum,width=20).grid(row = 0, column = 3, sticky = E)
    

    # 输入产品类型
    Label(root,text = r"产品类型:").grid(row = 1, column = 0,sticky = W)
    rad1 =Radiobutton(root, text=ptype1, variable=inputprdtype, value='MOD14A1')
    rad3 =Radiobutton(root, text=ptype3, variable=inputprdtype, value='MYD11A1')
    rad1.grid(row =1,column=1,sticky = W)
    rad3.grid(row =1,column=1,sticky = E)

    # 输入产品年份
    Label(root,text = r"年份选择:").grid(row = 2, column = 0,sticky = W)
    yearchosen = ttk.Combobox(root,width=10, textvariable=inputprddatey)
    yearchosen['values'] = (2017,2016,2015, 2014, 2013)
    yearchosen.current(0)
    yearchosen.grid(row =2,column =1,sticky = W)
    
    # 输入年积日
    Label(root,text = r"起始日期:").grid(row = 3,column =0, sticky = W)
    Entry(root, textvariable = inputprddatedbeg,width = 20).grid(row = 3, column = 1, sticky = W)
    Label(root,text = r"结束日期:").grid(row = 3,column =2, sticky = E)
    Entry(root, textvariable = inputprddatedend,width=20).grid(row = 3, column = 3, sticky = E)
    
    
    # 输出文件夹
    Label(root,text = r"输出位置:").grid(row = 5, column = 0, sticky = W)
    Entry(root, textvariable = outputPath,width=50).grid(row = 5,columnspan=3,column = 1)
    Label(root,text = '').grid(row = 5, column = 4)
    Button(root, text = r"选择...",width=10, command = selectOutPath).grid(row = 5, column = 5)
    Label(root,text = '').grid(row = 5, column = 6)


    # 开始处理按钮
    Button(root, text = r"开始下载",width=20, command = downprd).grid(row = 6, column = 3)

    # 已下载数据
    
    Label(root).grid(row = 7, column = 0)
    Label(root,text = r"已下载数据:").grid(row = 8, column = 0)
    prdlist=Listbox(root,width=50, selectmode=BROWSE )
    prdlist.grid(row =8,columnspan =3,column =1)
    scrl = Scrollbar(root)
    scrl.grid(row =8,column =4,sticky = N+S+W,columnspan=2)
    prdlist.configure(yscrollcommand = scrl.set)

    root.mainloop()
