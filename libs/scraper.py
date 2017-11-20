import sys
sys.path.append('.\libs\scraperlibs')
import pageRet, fileIO, wordSearcher, findPosts, findDates, findTitle
class page:
    '''For storing and retrieving pages, with lots of functions for manipulating them'''
    def __init__(self, url):
        self.search = wordSearcher.wordSearcher
        self.raw = pageRet.pageRet(url).decode()
        self.url = url
        ignoreChars = False
        text = ""
        for char in self.raw: #remove all HTML tags
            if char == "<":
                ignoreChars = True
            elif char == ">":
                ignoreChars = False
            elif not ignoreChars:
                text += str(char)
        self.text = text
    def findFirstPost(self):
        '''() -> str : url
        find first post in a forum section'''
        return findPosts.FirstPost(self.raw)

    def findAllPosts(self):
        '''() -> list of str : url
        find all posts in a forum section'''
        return findPosts.FindPosts(self.raw)

    def findDates(self):
        '''() -> list of struct_time
        find all post dates in a post'''
        return findDates.findDates(self.text)

    def findTitle(self):
        '''() -> str
        finds text between <title> and </title>'''
        return findTitle.findTitle(self.raw)

    def findTopicTitle(self):
        '''() -> str
        finds topic title'''
        fullTitle = self.findTitle()
        topicTitle = fullTitle[wordSearcher.wordSearcher(" Topic: ", fullTitle, output="lastchar")[0]:]
        return topicTitle

    def searchraw(self, string):
        '''(str) -> list of int
        search self.raw for string, returns locations in self.raw'''
        return wordSearcher.wordSearcher(string, self.raw)

    def searchtext(self, string):
        '''(str) -> list of int
        search self.text for string, returns locations in self.text'''
        return wordSearcher.wordSearcher(string, self.text)
