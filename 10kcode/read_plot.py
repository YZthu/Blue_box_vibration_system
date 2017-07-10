import numpy as np
import matplotlib.pyplot as plt

filename = 'test.txt'
f = open(filename,'rb')
testnum = 10
x = np.linspace(0,255*testnum-1,255*testnum)
data = np.linspace(0,0,255*testnum)
count = 0
for kk in f.readlines():
    tmpdata = kk.split(' ')
    L = len(tmpdata)
    print 'L is %d'%L
    for jj in range(1,L):
        data[count] = int(tmpdata[jj])
        count +=1
    if count >= 255*testnum-1:
        break

f.close()

plt.figure(figsize=(8,4))
plt.plot(x,data,color='red',linewidth=1)
plt.xlabel("Time")
plt.ylabel("Viberation")
plt.show()

       

