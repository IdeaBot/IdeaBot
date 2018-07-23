"""This is for opening and closing files with a few other features tucked in
for fun"""
def addToFile(filename, information, overwrite=False):
    '''(str, str [, bool]) -> True
    add content to the end of a file, or create a new file'''
    if overwrite:
        file = open(filename, "w")
        file.write(information)
        file.close()
    else:
        try:
            file = open(filename, "r")
            filetowrite =file.read()+information
            file.close()
            file = open(filename, "w")
            file.write(filetowrite)
            file.close()
        except:
            file = open(filename, "w")
            file.write(information)
            file.close()
    return True

def retrieveFile(filename, binary=False):
    '''(str [, bool]) -> str
    retrieve file at location filename, return file contents'''
    if binary:
        file = open(filename, "rb")
    else:
        file = open(filename, "r")
    fileInfo = file.read()
    file.close() #always close your files, kids!
    return fileInfo

def retrieveFileLines(filename, binary=False):
    '''(str [, bool]) -> list of str
    retrieve file a location filename, return file line by line'''
    if binary:
        file = open(filename, "rb")
    else:
        file = open(filename, "r")
    fileInfo = file.readlines()
    file.close() #always close your files, kids!
    return fileInfo

def writeFile(filename, information, binary=False, returnFile=False):
    '''(str, str [, bool, bool]) -> str (if returnFile == True) or True
    write information to file a location filename'''
    if binary:
        file = open(filename, "wb")
    else:
        file = open(filename, "w")
    file.write(information)
    file.close()
    if returnFile:
        if binary:
            file = open(filename, "rb")
            fileInfo=file.read()
        else:
            file = open(filename, "r")
            fileInfo=file.read()
        file.close()
        return fileInfo
    else:
        return True
