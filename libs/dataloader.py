import configparser
class datafile: # loads and parses files depending on file ending
    def loadConfig(self, filename):
        '''() -> Config class
        load the config.txt file'''
        config = configparser.ConfigParser()
        config.read(filename)
        return config

    def loadRawText(self, filename):
        '''() -> list of str
        returns each file of the line as an element in the list'''
        file = open(filename, "r")
        return file.readlines()
    def saveRawText(self):
        '''() -> None
        save file as .txt or extensionless'''
        if self.type:
            file = open(self.name+"."+self.type, "w")
        else:
            file = open(self.name, "w")
        text = ""
        #print(self.content, "is being saved")
        for i in self.content:
            text+=i+"\n"
        file.write(text)
        file.close()

    def loadCSV(self, filename):
        '''() -> list of list of str
        splits the file by line and by comma'''
        contents = self.loadRawText(filename)
        contents = [i.split(",") for i in contents] # split at commas
        contents = [i.strip() for i in contents] # remove whitespaces (in case it was actuall seperated by ", ")
        return contents
    def saveCSV(self):
        '''() -> None
        saves file as CSV'''
        file = open(self.name+".csv", "w")
        text = ""
        for i in self.content:
            for j in i:
                text += j+","
            text+="\n"
        file.write(text)
        file.close()

    def __init__(self, filename):
        if "." in filename:
            fileExt = filename[len(filename)-filename[::-1].index("."):].lower()
            if fileExt == "config":
                self.content = self.loadConfig(filename)
            elif fileExt == "csv":
                self.content = self.loadCSV(filename)
            else:
                self.content = self.loadRawText(filename)
            self.type = fileExt
            self.name = filename[:len(filename)-filename[::-1].index(".")-1]
        else:
            self.content = self.loadRawText(filename)
            self.type = None
            self.name = filename
    def save(self):
        '''() -> None
        saves the file in the original format it was parsed from, including any chances'''
        if self.type == "csv":
            self.saveCSV()
        elif self.type != "config":
            self.saveRawText()
        # it's nasty saving Configs
    def contains(self, string):
        '''(str) -> bool
        searches for string in the content list strings
        Precondition: self.content must be a list of strings (no sublists or anything)
        (THIS WILL CRASH IF IT'S A CONFIG FILE!!!)'''
        for i in self.content:
            if string in i:
                return True
        return False

    def index(self, string):
        '''(str) -> (int, int)
        finds string in self.content, returns the location
        Precondition: self.content must be a list of strings (no sublists or anything)
        (THIS WILL CRASH IF IT'S A CONFIG FILE!!!)'''
        for i in range(len(self.content)):
            for j in range(len(self.content[i]-len(string))):
                if self.content[i][j:j+len(string)] == string:
                    return (i,j)
        return (-1, -1)
