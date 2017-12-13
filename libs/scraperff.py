from bs4 import BeautifulSoup
import dataloader, time, logging
import sys
sys.path.append('./libs/scraperlibs')
import pageRet

config = dataloader.datafile('./data/freeforums.config')
config.content = config.content["DEFAULT"]
print(config.content["datafilepath"])
data = dataloader.datafile(config.content["datafilepath"])

def forumLogging():
    '''() -> Logger class
    set ups main log so that it outputs to ./scraperf.log and then returns the log'''
    logger = logging.getLogger('forum')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='scraperf.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    return logger

forumLog = forumLogging()

def is_new_thread(url):
    '''(str) -> bool
    checks freeforums.txt for whether the url is new or not'''
    is_new = True
    if len(data.content) > 0:
        for i in range(len(data.content)):
            if data.content[i][:len("Most Recent Thread:")].lower() == "most recent thread:" : # if it's the file line about most recent thread
                if url == data.content[i][len("Most Recent Thread:"):len("Most Recent Thread:")+len(url)]:
                    is_new = False
                else:
                    break
    return is_new

def delete_entry(string):
    '''(str [, bool])->bool
    delete the first entry in data.content that contains string, if it exists'''
    for i in range(len(data.content)):
        if string.lower() in data.content[i].lower():
            del(data.content[i])
            return True
    return False

def continuousScrape(q, stop):
    '''(Queue object, Queue object) -> None
    checks continuously for changes in the freeforums. A [url (str), affected users(str)] object is reported through q when anything changes
    This should be run in a different thread since it is blocking (it's a fucking while loop ffs)
    stop.put(anything) will stop the loop'''
    forumLog.info("Thread started")
    mostrecentrunstart = -100000
    while stop.empty(): # run continuously unless there's something in stop
        if time.time() - mostrecentrunstart >= int(config.content["period"]):
            forumLog.info("Starting scraping run")
            mostrecentrunstart = time.time()
            rss = BeautifulSoup(pageRet.pageRet(config.content["url"]).decode(), "html.parser") # landing page
            items = rss.find_all("item")
            threads = [[x.find("guid").get_text(), x.find("title").get_text()] for x in items] # list of [url, thread title]

            if is_new_thread(threads[0][0]):
                for i in threads:
                    if is_new_thread(i[0]):
                        forumLog.info("New thread found: " + i[0])
                        #scrape stuff
                        recentThread = BeautifulSoup(pageRet.pageRet(i[0]).decode(),"html.parser")
                        authors = [x.find("a").get("href") for x in recentThread.find_all("div", class_="mini-profile")]
                        q.put([i[0], authors])
                    else:
                        break
                delete_entry("most recent thread:")
                data.content.append("most recent thread:" + threads[0][0])
                data.save()
                forumLog.info("Most recent thread is now: " + threads[0][0])
            forumLog.info("Finished scraping run in "+ str(time.time() - mostrecentrunstart))
    forumLog.info("Stopped")


# debug pls comment out everything under here if it isn't already
#continuousScrape(None,None)

#data.save()
