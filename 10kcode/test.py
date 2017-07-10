import os
import struct
import GetFileList as GF

filepath = 'data'
filelist = GF.GetFileList(filepath,'2')
L = len(filelist)

for kk in range(L):
    print os.path.isfile(filelist[kk])
