import urllib.request
page=""
def pageRet(url):
    '''(str) -> str
    return the webpage at url'''
    global page
    page = urllib.request.urlopen(url).read()
    return page
