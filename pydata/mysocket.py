import time
import GetFileList as GF
import socketsend as sd

while True:
    
    filelist = GF.GetFileList('data','2')
    L = len(filelist)
    for ii in range(L):
        filepath = filelist[ii]
        if sd.socketsend(filepath) ==1:
            print'1111'
            continue
        else:
            print 'Err'
            break
    break
    time.sleep(100)
