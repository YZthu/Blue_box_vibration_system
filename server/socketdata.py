#-*_ coding:UTF-8 -*-

import socket,time,SocketServer,struct,os,thread
host='192.168.1.199'
port=9000
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM) #定义socket类型
s.bind((host,port)) #绑定需要监听的Ip和端口号，tuple格式
s.listen(1)
 
def conn_thread(connection,address):  
    while True:
        try:
            connection.settimeout(60)
            fileinfo_size=struct.calcsize('42s') 
            buf = connection.recv(fileinfo_size)
            if buf: #如果不加这个if，第一个文件传输完成后会自动走到下一句
                fileinfo = struct.unpack('42s',buf)
                tmpfi = str(fileinfo[0]).split(' ')
                
                tmpfiname = tmpfi[0]
                tmpfisize = tmpfi[1]
                filename = str(tmpfiname)
                filesize = int(str(tmpfisize).replace("',)",''))
                filename_f = filename.replace('data/','')
                fileday = str(filename_f.split('_')[0])
                newfilepath = str(address[0]) +'/'+fileday
                if os.path.isdir(newfilepath):
                    pass
                else:
                    os.mkdir(newfilepath)
                filenewname = os.path.join(newfilepath+'/',('new_'+ filename_f))
                print 'file new name is %s, filesize is %s' %(filenewname,filesize)
                recvd_size = 0 #定义接收了的文件大小
                file = open(filenewname,'wb')
                print 'stat receiving...'
                while not recvd_size == filesize:
                    if filesize - recvd_size > 1024:
                        rdata = connection.recv(1024)
                        recvd_size += len(rdata)
                    else:
                        rdata = connection.recv(filesize - recvd_size) 
                        recvd_size = filesize
                    file.write(rdata)
                file.close()
                print 'receive done'
                #connection.close()
        except socket.timeout:
            connection.close()

while True:
    connection,address=s.accept()
    print address[0]
    if os.path.isdir(address[0]):
        pass
    else:
        os.mkdir(address[0])

    #thread = threading.Thread(target=conn_thread,args=(connection,address)) #使用threading也可以
    #thread.start()
    thread.start_new_thread(conn_thread,(connection,address)) 
#    conn_thread(connection,address)

s.close()
