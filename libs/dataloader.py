'''
An attempt at a one-size-fits-all file handler. Depending on the file ending,
the way the file is loaded is automatically determined.

dataloader currently supports the following file extensions (loaded as):
.json (JSON)
.txt (Raw Text)
.csv (Comma-Seperated Values)
.config (config; handled by configparser python lib)
.db (SQLite 3)*

*SQLite support is very primitive atm

@author: NGnius
'''

import configparser, json, sqlite3
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
        result = file.readlines()
        result = [x if x[-1]!='\n' else x[:-1] for x in result] # remove page returns and other whitespace around lines
        file.close()
        return result
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
            if i!="":
                text+=i+"\n"
        file.write(text)
        file.close()

    def loadCSV(self, filename):
        '''() -> list of list of str
        splits the file by line and by comma'''
        contents = self.loadRawText(filename)
        contents = [i.split(",") for i in contents] # split at commas
        contents = [[y.strip() for y in i] for i in contents] # remove whitespaces (in case it was actuall seperated by ", ")
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

    def loadJSON(self, filename, default_val=list()):
        '''(str) -> dict or list or other iterable (depending on input)
        returns the filename interpreted as JSON'''
        file = open(filename)
        try:
            contents = json.load(file)
        except json.decoder.JSONDecodeError:
            contents = default_val
        file.close()
        return contents
    def saveJSON(self):
        '''() -> None
        saves file as JSON'''
        file = open(self.name+".json", "w")
        json.dump(self.content, file, ensure_ascii=False, indent=4)
        file.close()

    def loadDB(self, filename):
        '''(str) -> SQLite database
        opens an existing SQLite db'''
        connection = sqlite3.connect(filename)
        self.cursor = connection.cursor()
        self.execute = self.cursor.execute
        return connection
    def saveDB(self):
        '''() -> None
        commit changes to db'''
        self.content.commit()

    def __init__(self, filename, load_as=None, default_val=list()):
        if "." in filename:
            fileExt = filename[len(filename)-filename[::-1].index("."):].lower()
            if (fileExt == "config" and load_as==None) or load_as == "config":
                self.content = self.loadConfig(filename)
            elif (fileExt == "csv" and load_as==None) or load_as == "csv":
                self.content = self.loadCSV(filename)
            elif (fileExt == "json" and load_as==None) or load_as == "json":
                self.content = self.loadJSON(filename, default_val=default_val)
            elif (fileExt == "db" and load_as==None) or load_as == "db":
                self.content = self.loadDB(filename)
            else:
                self.content = self.loadRawText(filename)
            self.type = fileExt
            self.name = filename[:len(filename)-filename[::-1].index(".")-1]
        else:
            self.content = self.loadRawText(filename)
            self.type = None
            self.name = filename
        self.filename = filename

    def save(self, save_as=None):
        '''() -> None
        saves the file in the original format it was parsed from, including any chances'''
        if (self.type == "csv" and save_as==None) or save_as == "csv":
            self.saveCSV()
        elif (self.type == "json" and save_as==None) or save_as == "json":
            self.saveJSON()
        elif (self.type == "db" and save_as==None) or save_as=="db":
            self.saveDB()
        elif (self.type != "config" and save_as!=None) or save_as!="config":
            self.saveRawText()
        else:
            # it's nasty saving Configs
            pass

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

class newdatafile (datafile):
    def __init__(self, filename):
        self.content = []
        if "." in filename:
            self.type = filename[filename.rindex(".")+1:]
            self.name = filename[:filename.rindex(".")]
        else:
            self.type = ""
            self.name = filename
        self.filename = filename

def loadfile_safe(filepath, **kwargs):
    try:
        return datafile(filepath, **kwargs)
    except FileNotFoundError:
        return newdatafile(filepath)
