from bs4 import BeautifulSoup
import dataloader, time
import sys
sys.path.append('.\scraperlibs')
import pageRet

config = dataloader.datafile('.\\data\\freeforums.config')
config.content = config.content["DEFAULT"]
print(config.content["datafilepath"])
data = dataloader.datafile(config.content["datafilepath"])
def scrapeSection(url):
    '''(str) -> list of list of str
    returns [url, [affected authors (str)]] for every page that has something new in it'''
    pass # for now it does nothing because this is hard
def continuousScrape(q, stop):
    '''(Queue object, Queue object) -> None
    checks continuously for changes in the freeforums. A [url (str), affected users(str)] object is reported through q when anything changes
    This should be run in a different thread since it is blocking (it's a fucking while loop ffs)
    stop.put(anything) will stop the loop'''
    while True: #stop.empty(): # run continuously unless there's something in stop

        rss = BeautifulSoup(pageRet.pageRet(config.content["url"]).decode(), "html.parser") # landing page
        links = rss.find_all("item")
        threads = [[x.find("guid").get_text(), x.find("title").get_text()] for x in links]
        print(threads[0][0])
        shouldScrape = True
        mostrecentexists = False
        if len(data.content) > 0:
            for i in range(len(data.content)):
                if data.content[i][:len("Most Recent Post:")].lower() == "most recent post:" : # if it's the file line about most recent thread
                    mostrecentexists = True
                    if threads[0][0] == data.content[i][len("Most Recent Post:"):len("Most Recent Post:")+len(threads[0][0])]:
                        shouldScrape = False
                    else:
                        data.content[i] = "most recent post:"+threads[0][0]
                        data.save() #yep, we save during the process, so that you get to wait even longer for your results! Yay
                        break #gotta save those clock cycles
        if mostrecentexists == False:
            data.content.append("most recent post:"+threads[0][0])

        if shouldScrape:
            #scrape stuff
            print("This means I should scrape things, yay!")
            recentThread = BeautifulSoup(pageRet.pageRet(threads[0][0]).decode(),"html.parser")
            authors = [x.find("a").get("href") for x in recentThread.find_all("div", class_="mini-profile")]
            print(authors)


# debug pls comment out everything under here if it isn't already
continuousScrape(None,None)

#data.save()
