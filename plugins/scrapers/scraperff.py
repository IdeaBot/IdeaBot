from bs4 import BeautifulSoup
from libs import dataloader, plugin, embed
import time, logging, traceback, discord
from plugins.scrapers.scraperlibs import pageRet

'''config = dataloader.datafile('./data/freeforums.config')
config.content = config.content["DEFAULT"]
print(config.content["datafilepath"])
data = dataloader.datafile(config.content["datafilepath"])'''

CHANNEL = 'channel'
FORUM_URL = r"http://ideahavers.freeforums.net/"

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

class Plugin(plugin.ThreadedPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.CHANNEL_ID = self.config[CHANNEL] # discord server channel ID for sending forum updates to


    async def action(self): # 1/3 of the old doChecks function in main.py
        threads = list()
        while not self.queue.empty():
            threads.append(self.queue.get())
        for thread in threads[::-1]:
            await self.send_message(discord.Object(id=self.CHANNEL_ID), embed=embed.create_embed(description="In: "+thread[0], author={"name" : thread[1][-1]["name"], "url" : FORUM_URL+thread[1][-1]["url"], "icon_url" : None}, footer={"text":"Forum", "icon_url":None}))
            # NOTE: mentionChain has been removed, since it wasn't used much and it was more annoying than useful

    def _threaded_action(self, queue, **kwargs):
        self.data = dataloader.datafile(self.config["datafilepath"])
        super()._threaded_action(queue, **kwargs)

    def threaded_action(self, q, **kwargs):
        forumLog.info("Starting scraping run")
        mostrecentrunstart = time.time()
        try:
            rss = BeautifulSoup(pageRet.pageRet(self.config["url"]).decode(), "html.parser") # landing page
            items = rss.find_all("item")
            threads = [[x.find("guid").get_text(), x.find("title").get_text()] for x in items] # list of [url, thread title]

            if self.is_new_thread(threads[0][0]):
                newestint = self.get_trailing_int(self.get_most_recent())
                for i in threads:
                    if self.get_trailing_int(i[0]) > newestint:
                        forumLog.info("New thread found: " + i[0])
                        #scrape stuff
                        recentThread = BeautifulSoup(pageRet.pageRet(i[0]).decode(),"html.parser")
                        authors = []
                        for x in recentThread.find_all("div", class_="mini-profile"):
                            try:
                                authors.append({"name" : x.find("a").get_text(),"url" : x.find("a").get("href"), "img" : x.find("div", class_="avatar").find("img").get("src")})
                            except AttributeError: # if author is a guest, x.find("a") will return a NoneType, and None.get("href") will raise an AttributeError
                                pass
                        #authors = [x.find("a").get("href") for x in recentThread.find_all("div", class_="mini-profile")]
                        q.put([i[0], authors])
                    else:
                        break
                self.delete_entry("most recent thread:")
                self.data.content.append("most recent thread:" + threads[0][0])
                self.data.save()
                forumLog.info("Most recent thread is now: " + threads[0][0])
            forumLog.info("Finished scraping run in "+ str(time.time() - mostrecentrunstart))
        except:
            # Prevent a failed run from crashing the whole thread
            # traceback.print_exc()
            forumLog.warning("Scraping run failed. Either the page has changed or the page is unavailable...")


    def is_new_thread(self, url):
        '''(str) -> bool
        checks freeforums.txt for whether the url is new or not'''
        is_new = True
        if len(self.data.content) > 0:
            for i in range(len(self.data.content)):
                if self.data.content[i][:len("Most Recent Thread:")].lower() == "most recent thread:" : # if it's the file line about most recent thread
                    if url[:-3] == self.data.content[i][len("Most Recent Thread:"):len("Most Recent Thread:")+len(url)][:-3]:
                        is_new = False
                    else:
                        break
        return is_new

    def has_new_stuff(self, url):
        if len(self.data.content) > 0:
            for i in range(len(self.data.content)):
                if self.data.content[i][:len("Most Recent Thread:")].lower() == "most recent thread:" : # if it's the file line about most recent thread
                    if url == self.data.content[i][len("Most Recent Thread:"):len("Most Recent Thread:")+len(url)]:
                        is_new = False
                    else:
                        break
        return is_new

    def get_most_recent(self):
        '''(None) -> str
        returns the url of the most recent thread in self.data.content'''
        for i in range(len(self.data.content)):
            if self.data.content[i][:len("Most Recent Thread:")].lower() == "most recent thread:" : # if it's the file line about most recent thread
                return self.data.content[i][len("Most Recent Thread:")+1:]

    def get_trailing_int(self, url):
        '''(str) -> int
        finds the integer at the end of RSS Proboard URLs
        eg http://ideahavers.freeforums.net/thread/42/answer-life-universe-everything-666 returns 666'''
        return int(url.split("-")[-1])


    def delete_entry(self, string):
        '''(str [, bool])->bool
        delete the first entry in self.data.content that contains string, if it exists'''
        for i in range(len(self.data.content)):
            if string.lower() in self.data.content[i].lower():
                del(self.data.content[i])
                return True
        return False
