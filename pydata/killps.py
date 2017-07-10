import os

def FindKillPs(psname):
    tmp = os.popen('ps -ef |grep ' + psname)
    allstr = tmp.read()
    print allstr
    alllist = allstr.split('\n')
    L = len(alllist)
    ID =''
    if L < 2:
        print"no such a process!"
        return 0
    breakflag = 0
    for ii in range(L-2):
        tmpstr = alllist[ii]
        if len(tmpstr) > 0:  #it's a process
            flag = 0
            for ii in tmpstr.split(' '):
                tmplen = len(ii)
                if flag ==1 and tmplen >0:
                    ID = ii
                    breakflag = 1             
                    break
                if tmplen > 0:
                    flag =1
        if breakflag == 1:
            break
    print 'ID is %s'%ID
    if ID !='':
        print "GG"
        os.popen('kill '+ ID)
 
if __name__ =='__main__':
        
    FindKillPs('readcom_anchor.py')
