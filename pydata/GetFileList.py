
def IsSubString(SubStrList,Str):

    flat = True
    for substr in SubStrList:
        if not(substr in Str):
            flat = False
    return flat

#################

def GetFileList(FindPath,FlagStr = []):
    import os
    FileList = []
    FileNames = os.listdir(FindPath)
    if (len(FileNames)>0):
        for fn in FileNames:
            if (len(FlagStr)>0):
                if (IsSubString(FlagStr,fn)):
                    fullfilename = os.path.join(FindPath,fn)
                    FileList.append(fullfilename)
            else:
                fullfilename = os.path.join(FindPath,fn)
                FileList.append(fullfilename)
    if (len(FileList)>0):
        FileList.sort()
    return FileList


if __name__ == '__main__':
    print GetFileList('data','20')
