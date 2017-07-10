import struct
import binascii
import ctypes
import numpy as np

s = struct.Struct('s')

f = open('../newdata/2017-06-28 14:30:04.850733.txt','rb')
wfile = open('test.txt','w')

data = f.read()
L = len(data)
print 'L is %d'%L

databuffer = ctypes.create_string_buffer(L)
tmpbuffer = ctypes.create_string_buffer(1)
tmpbuffer2 = ctypes.create_string_buffer(1)

con = 2**8
ffff = con*con -1
ii =0
usefulcount =0
maxdata =0
tmpdataarray = np.linspace(0,0,260)
datastr = ''
while ii <L-1:
#s.pack_into(databuffer,ii,data[ii])
    s.pack_into(tmpbuffer, 0, data[ii]) 
    s.pack_into(tmpbuffer2, 0, data[ii+1])
    highbits = int(binascii.hexlify(tmpbuffer),16)
    lowbits = int(binascii.hexlify(tmpbuffer2),16)
    tmpdata = highbits*con + lowbits
    if tmpdata > maxdata:
        maxdata = tmpdata
    if tmpdata >= ffff:  #we get a start
        if ii+2+512 > L:   #not enough
            print 'Err'
            break
        kk = ii+2
        while kk < ii+2+510:
            s.pack_into(tmpbuffer, 0, data[kk]) 
            s.pack_into(tmpbuffer2, 0, data[kk+1])
            lowbits = int(binascii.hexlify(tmpbuffer),16)
            highbits = int(binascii.hexlify(tmpbuffer2),16)
            tmpdata = highbits*con + lowbits
            tmpdataarray[(kk-ii-2)/2 + 1] = tmpdata
            datastr += ' '+str(tmpdata)
            kk += 2
            #save data
        wfile.write(datastr)
        datastr = ''
        wfile.write('\n')
        
        ii += 511
        usefulcount +=1
    ii +=1
print 'usefulcount is %d'%usefulcount
print 'maxdata is %d'%maxdata
#print binascii.hexlify(databuffer)
f.close()
'''
for data in f.readlines():
	L = len(data)
	print L
	if L == 0:
	    continue
	databuffer = ctypes.create_string_buffer(L)
	for ii in range(L):
		s.pack_into(databuffer,ii,data[ii])
	break

print binascii.hexlify(databuffer)
'''

