import pipes
import os
import subprocess
import GetFileList as GF
import getIp as GP
import time
import thread

def myrsync(filepath,serverpath):
    #ssh_host='kevin@192.168.1.199'
    global ssh_host
    com = 'rsync -arvz '+ filepath +' '+ssh_host+serverpath
    resp = subprocess.call(com, shell=True)
    return resp ==0
    if resp!=0:
        print"something wrong!"
    else:
        print"rsync successful!"

def checkfile(filename):
    #ssh_host='kevin@192.168.1.199'
    global ssh_host
    filepath = filename
    com = 'ssh '+ ssh_host + ' test -s '+pipes.quote(filepath)
    #print com
    resp = subprocess.call(com, shell=True)
    return resp ==0
    if resp==0:
        print"we get it!"
    else:
        print"fail!"

def sendfile():
    #get Ip address
    #IP = GP.getIp('eth0')
    global IP
    filelist = GF.GetFileList('data','2')
    L = len(filelist)
    global hfspath
    for ii in range(L):
        tmpfile = filelist[ii]
        filename = str(tmpfile.split('/')[1])
        #print "filename is %s"%filename
        filedate = str(filename.split('_')[0])
        #print "filedate is %s"%filedate
        serverpath = hfspath + IP + '/' + filedate +'/'
        filepath = tmpfile
        #print "serverpath is %s"%serverpath
        #print "filepath is %s"%filepath
        sendflag = myrsync(filepath, serverpath)
        if sendflag ==1:
            #send success
            tmpfilepath=serverpath.replace(':','')+filename
            checkflag = checkfile(tmpfilepath)
            #print serverpath+filename
            #print checkflag
            if checkflag ==1:
                #delete this file
                #print "tmpfilepath is %s"%filepath
                if os.path.exists(filepath):
                    #print 'GG'
                    os.remove(filepath)
                    pass
                else:
                    print "no such file, delete err!"
            else:
                #do not delete
                pass
        else:
            #send err do something to help it
            pass
    
def mysendfile():
    while True:
        sendfile()        
        time.sleep(100)

if __name__ =='__main__':
    ssh_host='kevin@192.168.1.199'
    hfspath =':/home/kevin/Desktop/'
    IP = GP.getIp('eth0')
        
  # myrsync('data/1.txt','123')
    thread.start_new_thread(mysendfile,())
    while True:
        time.sleep(100)
