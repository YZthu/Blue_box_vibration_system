import os
import subprocess
import sys
import time
def MkIpDir():
    global Ipgat 
    global startIp 
    global allnum 
    
    tmpIp = startIp
    for ii in range(allnum):
         dirname = Ipgat + str(tmpIp)
         tmpIp += 1
         os.mkdir(dirname)

def CountFile(filepath):
    dirlist = os.listdir(filepath)
    print len(dirlist)
    count = 0
    for ii in dirlist:
        print ii
        if os.path.isfile(filepath+'/'+ii):
            count += 1
        else:
            count = count + CountFile(filepath+'/' +ii)
    return count

def MonitSensor():
    global Ipgat
    global startIp
    global allnum
    f = open('sensor.txt','w')
    ping_time = time.strftime('%Y-%m-%d_%X',time.localtime())
    f.write(str(ping_time)+'\n')
    tmpadd = startIp
    for ii in range(allnum):
        IP = Ipgat + str(tmpadd)	
        result = os.system('ping -c 1 %s'%IP)
        if result ==0:
            f.write(IP + '   ' + 'live\n')
            print'%s is ok'%IP
        else:
            f.write(IP + '   ' + 'down\n')
            print '%s bradkdown'%IP
        tmpadd +=1
    f.close()
    

if __name__ =='__main__':
    
    Ipgat = '192.168.1.'
    startIp = 211
    allnum = 10
    MonitSensor() 
    #MkIpDir() #generate dir for save data
    #print CountFile('192.168.1.211')
