from bs4 import BeautifulSoup
from libs import dataloader, plugin, embed
import time, logging, traceback, discord
from plugins.scrapers.scraperlibs import pageRet

'''config = dataloader.datafile('./data/freeforums.config')
config.content = config.content["DEFAULT"]
print(config.content["datafilepath"])
data = dataloader.datafile(config.content["datafilepath"])'''

CHANNEL = 'channel'
CHANNELS = 'channels'
FORUM_URL = r"http://ideahavers.freeforums.net/"
MOST_RECENT = 'most-recent'
FIRST = 'aaa-000'

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

class Plugin(plugin.ThreadedPlugin, plugin.Multi):
    '''Multithreaded plugin for scraping Proboards (freeforums)

    This currently only works with a single forum - the Idea Project forum '''
    def __init__(self, **kwargs):
        super().__init__(should_spawn_thread=False, **kwargs)
        self.CHANNEL = CHANNEL
        self.CHANNELS = CHANNELS
        self.MOST_RECENT = MOST_RECENT
        self.FIRST = FIRST
        self.data = dataloader.loadfile_safe(self.config["datafilepath"])
        if not isinstance(self.data.content, dict):
            self.data.content = dict()
        self.threaded_kwargs = {"newForum":self.public_namespace.newProBoardsForum}
        self.spawn_process()

    def threaded_action(self, q, newForum=plugin.Queue(), **kwargs):
        # handle new items from url_adder
        while not newForum.empty():
            item = newForum.get()
            if item["action"] == "remove" or item["action"] == "delete":
                try:
                    del(self.data.content[item["url"]][self.CHANNELS][self.data.content[item["url"]][self.CHANNELS].index(item[self.CHANNEL])])
                    if self.data.content[item["url"]][self.CHANNELS] == list():
                        del(self.data.content[item["url"]])
                except (TypeError, KeyError, ValueError, NameError):
                    # traceback.print_exc()
                    pass
            elif item["action"]=="add":
                forumLog.debug("Adding "+item['url'])
                if not item['url'].endswith(r"/rss/public"):
                    item['url'].strip(r"/")
                    item['url']+=r"/rss/public"
                if item["url"] not in self.data.content:
                    self.data.content[item["url"]]={self.CHANNELS:list(), self.MOST_RECENT:self.FIRST} # dict
                self.data.content[item["url"]][self.CHANNELS].append(item[self.CHANNEL])
        # do scrape things
        for forum in self.data.content:
            forumLog.debug("Now scraping %s" %forum)
            mostrecentrunstart = time.time()
            try:
                rss = BeautifulSoup(pageRet.pageRet(forum).decode(), "html.parser") # landing page
                items = rss.find_all("item")
                threads = [[x.find("guid").get_text(), x.find("title").get_text()] for x in items] # list of [url, thread title]

                if self.is_new_thread(threads[0][0], forum):
                    newestint = self.get_trailing_int(self.get_most_recent(forum))
                    if self.get_most_recent(forum)==self.FIRST:
                        threads=[threads[0]]
                    for i in threads:
                        if self.get_trailing_int(i[0]) > newestint:
                            forumLog.debug("New thread found: " + i[0])
                            #scrape stuff
                            recentThread = BeautifulSoup(pageRet.pageRet(i[0]).decode(),"html.parser")
                            authors = []
                            for x in recentThread.find_all("div", class_="mini-profile"):
                                try:
                                    authors.append({"name" : x.find("a").get_text(),"url" : x.find("a").get("href"), "img" : x.find("div", class_="avatar").find("img").get("src")})
                                except AttributeError: # if author is a guest, x.find("a") will return a NoneType, and None.get("href") will raise an AttributeError
                                    pass
                            #authors = [x.find("a").get("href") for x in recentThread.find_all("div", class_="mini-profile")]
                            thread = [i[0], authors]
                            for discord_channel in self.data.content[forum][self.CHANNELS]:
                                q.put({self.SEND_MESSAGE:
                                        {plugin.ARGS:[discord.Object(id=discord_channel)],
                                        plugin.KWARGS:{'embed':embed.create_embed(description="In: "+thread[0], author={"name" : thread[1][-1]["name"], "url" : forum+thread[1][-1]["url"], "icon_url" : None}, footer={"text":"Forum", "icon_url":None})}}})
                                # q.put([i[0], authors])
                        else:
                            break
                    # self.delete_entry("most recent thread:", forum)
                    self.data.content[forum][self.MOST_RECENT]= threads[0][0]
                    forumLog.debug("Most recent thread is now: " + threads[0][0])
                forumLog.debug("Finished scraping run in "+ str(time.time() - mostrecentrunstart))
            except:
                # Prevent a failed run from crashing the whole thread
                # traceback.print_exc()
                forumLog.warning("Scraping run failed for %s. Either the page has changed or the page is unavailable..." %forum)
        self.data.save()


    def is_new_thread(self, url, forum):
        '''(str) -> bool
        checks freeforums.txt for whether the url is new or not'''
        most_recent = self.get_most_recent(forum)
        return most_recent!=url
        '''
        if len(self.data.content[forum]) > 0:
            for i in range(len(self.data.content)):
                if self.data.content[forum][i][:len("Most Recent Thread:")].lower() == "most recent thread:" : # if it's the file line about most recent thread
                    if url[:-3] == self.data.content[forum][i][len("Most Recent Thread:"):len("Most Recent Thread:")+len(url)][:-3]:
                        is_new = False
                    else:
                        break
        return is_new

    def has_new_stuff(self, url, forum):
        most_recent = self.get_most_recent(forum)
        return most_recent!=url
        if len(self.data.content[forum]) > 0:
            for i in range(len(self.data.content[forum])):
                if self.data.content[forum][i][:len("Most Recent Thread:")].lower() == "most recent thread:" : # if it's the file line about most recent thread
                    if url == self.data.content[forum][i][len("Most Recent Thread:"):len("Most Recent Thread:")+len(url)]:
                        is_new = False
                    else:
                        break
        return is_new'''

    def get_most_recent(self, forum):
        '''(None) -> str
        returns the url of the most recent thread in self.data.content'''
        return self.data.content[forum][self.MOST_RECENT]
        for i in range(len(self.data.content)):
            if self.data.content[forum][i][:len("Most Recent Thread:")].lower() == "most recent thread:" : # if it's the file line about most recent thread
                return self.data.content[forum][i][len("Most Recent Thread:")+1:]

    def get_trailing_int(self, url):
        '''(str) -> int
        finds the integer at the end of RSS Proboard URLs
        eg http://ideahavers.freeforums.net/thread/42/answer-life-universe-everything-666 returns 666'''
        return int(url.split("-")[-1])


    def delete_entry(self, string, forum):
        '''(str [, bool])->bool
        delete the first entry in self.data.content that contains string, if it exists'''
        for i in range(len(self.data.content[forum])):
            if string.lower() in self.data.content[forum][i].lower():
                del(self.data.content[forum][i])
                return True
        return False
