
import os
import socket,fcntl,struct

def getIp(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(),0x8915,struct.pack('256s',ifname[:15]))[20:24])

if __name__=='__main__':
    print getIp('eth0')
    print getIp('lo')
