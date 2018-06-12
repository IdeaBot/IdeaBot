from bs4 import BeautifulSoup
from libs import dataloader
import time, logging
import sys
sys.path.append('./libs/scraperlibs')
import pageRet

CONFIG_LOC = './data/twitter.config'

config = dataloader.datafile(CONFIG_LOC)
config.content = config.content["DEFAULT"]
print(config.content["datafilepath"])
data = dataloader.datafile(config.content["datafilepath"])
def tweetLogging():
    '''() -> Logger class
    set ups main log so that it outputs to ./scrapert.log and then returns the log'''
    logger = logging.getLogger('twitter')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='scrapert.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    return logger

twitLog = tweetLogging()

def get_tweet(bso):
    '''(BeautifulSoup object) -> str
    gets the text from title'''
    return bso.find("title").get_text()
def get_url(bso):
    '''(BeautifulSoup object) -> str
    gets the text from guid'''
    return bso.find("guid").get_text()
def is_new_tweet(url, second=False):
    '''(str [, bool]) -> bool
    returns True if the url is new, False otherwise'''
    is_new = True
    if len(data.content) > 0:
        for i in range(len(data.content)):
            if data.content[i][:len("Most Recent Tweet:")].lower() == "most recent tweet:" and not second: # if it's the file line about most recent thread
                if url == data.content[i][len("Most Recent Tweet:"):len("Most Recent Tweet:")+len(url)]:
                    is_new = False
            if data.content[i][:len("Second Most Recent Tweet:")].lower() == "second most recent tweet:" :
                if url == data.content[i][len("Second Most Recent Tweet:"):len("Second Most Recent Tweet:")+len(url)]:
                    is_new = False

    return is_new
def delete_entry(string):
    '''(str)->bool
    delete the first entry in data.content that contains string, if it exists'''
    for i in range(len(data.content)):
        if string.lower() in data.content[i].lower():
            del(data.content[i])
            return True
    return False

def get_author(bso):
    '''(BeautifulSoup object) -> str
    find the author's twitter handle '''
    return bso.find("dc:creator").get_text().strip(" (@)")

def get_author_from_url(url):
    '''(str) -> str
    find the author's twitter handle in the url'''
    return url.split("=")[-1].strip("/")

def continuousScrape(q, stop):
    '''(Queue object, Queue object) -> None
    checks continuously for new tweets from the official twitter. A [url (str), tweet (str)] object is reported through q when anything changes
    This should be run in a different thread since it is blocking (it's a while loop ffs)
    stop.put(anything) will stop the loop'''
    twitLog.info("Thread started")
    mostrecentrunstart = -999999
    author = get_author_from_url(config.content["url"])
    while stop.empty(): # run continuously unless there's something in stop
        if time.time() - mostrecentrunstart >= int(config.content["period"]):
            twitLog.info("Starting scraping run")
            mostrecentrunstart = time.time()
            try:
                rss = BeautifulSoup(pageRet.pageRet(config.content["url"]).decode(), "html.parser") # rss page
                items = rss.find_all("item")
                #print(items)
                tweets = [[get_url(x), get_tweet(x), x] for x in items] # create list of [url to tweet, tweet content]
                pinned_tweet = tweets[0]
                tweets = tweets[1:] # remove first tweet since it's pinned

                if len(tweets)>1 and is_new_tweet(tweets[0][0]) and is_new_tweet(tweets[1][0], second=True):
                    for i in tweets:
                        if is_new_tweet(i[0]):
                            twitLog.info("New tweet found: " + i[0])
                            tweet_author = get_author(i[2])
                            q_entry = {"url":i[0], "content":i[1], "author":tweet_author, "retweet":False}
                            if author != tweet_author:
                                q_entry["retweet"] = True
                            q.put(q_entry)
                        else:
                            break
                    delete_entry("most recent tweet:")
                    data.content.append("most recent tweet:"+tweets[0][0])
                    data.content.append("second most recent tweet:"+tweets[1][0])
                    data.save()
                    twitLog.info("Most recent tweet is now: " + tweets[0][0])
                    twitLog.info("Second most recent tweet is now: " + tweets[1][0])
                twitLog.info("Finished scraping run in "+ str(time.time() - mostrecentrunstart))
            except:
                twitLog.warning("Scraping run failed. Either the page has changed or the page is unavailable...")
    twitLog.info("Stahped")



# debug pls comment out everything under here if it isn't already
#continuousScrape(None,None)

#data.save()
