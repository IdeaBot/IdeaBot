from bs4 import BeautifulSoup
import dataloader, time
import sys
sys.path.append('.\\libs\\scraperlibs')
import pageRet

config = dataloader.datafile('.\\data\\twitter.config')
config.content = config.content["DEFAULT"]
print(config.content["datafilepath"])
data = dataloader.datafile(config.content["datafilepath"])
def get_tweet(bso):
    '''(BeautifulSoup object) -> str
    gets the text from title'''
    return bso.find("title").get_text()
def get_url(bso):
    '''(BeautifulSoup object) -> str
    gets the text from guid'''
    return bso.find("guid").get_text()
def is_new_tweet(url):
    '''(str) -> bool
    returns True if the url is new, False otherwise'''
    is_new = True
    if len(data.content) > 0:
        for i in range(len(data.content)):
            if data.content[i][:len("Most Recent Tweet:")].lower() == "most recent tweet:" : # if it's the file line about most recent thread
                if url == data.content[i][len("Most Recent Tweet:"):len("Most Recent Tweet:")+len(url)]:
                    is_new = False
                else:
                    break
    return is_new
def continuousScrape(q, stop):
    '''(Queue object, Queue object) -> None
    checks continuously for new tweets from the official twitter. A [url (str), tweet (str)] object is reported through q when anything changes
    This should be run in a different thread since it is blocking (it's a fucking while loop ffs)
    stop.put(anything) will stop the loop'''
    while stop.empty(): # run continuously unless there's something in stop

        rss = BeautifulSoup(pageRet.pageRet(config.content["url"]).decode(), "html.parser") # rss feed page
        items = rss.find_all("item")
        threads = [[get_url(x), get_tweet(x)] for x in items] # create lsit of [url to tweet, tweet content]
        print(threads[0][0])

        if mostrecentexists == False:
            data.content.append("most recent tweet:"+threads[0][0])

        if shouldScrape:
            #scrape stuff
            print("This means I should scrape things, yay!")
            recentThread = BeautifulSoup(pageRet.pageRet(threads[0][0]).decode(),"html.parser")
            authors = [x.find("a").get("href") for x in recentThread.find_all("div", class_="mini-profile")]
            print(authors)
            q.put([threads[0][0], authors])


# debug pls comment out everything under here if it isn't already
#continuousScrape(None,None)

#data.save()
