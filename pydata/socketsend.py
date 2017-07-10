def socketsend(filepath):
#-*- coding: UTF-8 -*-
    import socket,os,struct
    result = 0
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect(('192.168.1.199',9000)) #server's IP and port number
    while True: 
        L = len(filepath)
        if os.path.isfile(filepath):
            #fileinfo_size=struct.calcsize('37s')
            headinfo=filepath +' '+ str(os.stat(filepath).st_size)
            L = len(headinfo)
            print L
            tmpfnt = str(L)+'s'
            fhead = struct.pack(tmpfnt,headinfo)
            print 'filesize is %d'%os.stat(filepath).st_size
            s.send(fhead) 
            print 'client filepath: ',filepath
            fo = open(filepath,'rb')
            count = 0
            while True:
                filedata = fo.read(1024)
                if not filedata:
                    break
                s.send(filedata)
                count +=1
            fo.close()
            print count
            print 'send over...'
           #s.close()
        result = 1
        break
    return result
