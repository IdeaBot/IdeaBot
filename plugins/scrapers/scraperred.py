from bs4 import BeautifulSoup
from libs import dataloader, plugin, embed
import time, logging, sys, discord, traceback
from plugins.scrapers.scraperlibs import pageRet

URL = 'url'
CHANNEL = 'channel'
CHANNELS = 'channels'
SEEN = 'seen'
REDDIT_LOGO = r"https://pbs.twimg.com/profile_images/868147475852312577/fjCSPU-a_400x400.jpg" #ignore that this is a Twitter link *whistles innocently*
SLOWDOWN = 0

def redditLogging():
    '''() -> Logger class
    set ups main log so that it outputs to ./scraperr.log and then returns the log'''
    logger = logging.getLogger('reddit')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='scraperr.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    return logger

redditLog = redditLogging()

class Plugin(plugin.ThreadedPlugin):
    '''Multithreaded plugin for scraping the front page of the internet. Or at least certain parts of Reddit

    **Usage:**
    ```@Idea (add or remove) <url> ``` '''
    def __init__(self, **kwargs):
        super().__init__(should_spawn_thread=False, **kwargs)
        self.data = dataloader.loadfile_safe(self.config["datafilepath"])
        if not isinstance(self.data.content, dict):
            self.data.content = dict()
        # self.data.content = [x.strip("\n") for x in self.data.content]
        # self.urllist = dataloader.loadfile_safe(self.config["urlfilepath"])
        # self.urllist.content = [x.strip("\n") for x in self.urllist.content]
        self.threaded_kwargs = {"newThread":self.public_namespace.newRedditThread}
        # self.CHANNEL_ID = self.config[CHANNEL]
        self.CHANNELS = CHANNELS
        self.CHANNEL = CHANNEL
        self.SEEN = SEEN
        self.spawn_process()

    def threaded_action(self, q, newThread=plugin.Queue(), **kwargs):
        '''(Queue object, Queue object, Queue object) -> None
        checks continuously for changes in the watched reddit pages.
        A [url (str), affected users(str)] object is reported through q when anything changes
        This should be run in a different thread since it is blocking (it's a fucking while loop ffs)'''

        while not newThread.empty():
            item = newThread.get()
            if not item["url"].strip("/").endswith(".rss?sort=new"):
                item["url"] = item["url"].strip("/")+".rss?sort=new"
            if item["action"] == "remove" or item["action"] == "delete":
                try:
                    del(self.data.content[item["url"]][self.CHANNELS][self.data.content[item["url"]][self.CHANNELS].index(item[self.CHANNEL])])
                    if self.data.content[item["url"]][self.CHANNELS] == list():
                        del(self.data.content[item["url"]])
                    redditLog.debug(item["url"]+" successfully removed from channel "+item[self.CHANNEL])
                except (TypeError, KeyError, ValueError, NameError):
                    # traceback.print_exc()
                    redditLog.debug(item["url"]+" wasn't found nor removed")
            elif item["action"]=="add":
                if item["url"] not in self.data.content:
                    self.data.content[item["url"]]={self.SEEN:[], self.CHANNELS:[]}
                    redditLog.debug(item["url"]+" successfully created")
                self.data.content[item["url"]][self.CHANNELS].append(item[self.CHANNEL])
                redditLog.debug(item["url"]+" successfully added to "+item[self.CHANNEL])
        # self.data.save()

        redditLog.debug("Starting scraping run")
        mostrecentrunstart = time.time()
        for url in self.data.content:
            redditLog.info("Now scraping " + url)
            try:
                rss = BeautifulSoup(pageRet.pageRet(url).decode(), "html.parser") # rss page
                items = rss.find_all("entry")[1:]
                comments = [[x.find("link").get("href"), x.find("title").get_text()] for x in items] # list of [url, thread title]

                if self.is_new_comment(comments[0][0], url):
                    redditLog.debug("New response found: " + comments[0][0])
                    self.data.content[url][self.SEEN].append(comments[0][0])
                    comment = [url[:-len(".rss?sort=new")], comments[0][0]]
                    for discord_channel in self.data.content[url][self.CHANNELS]:
                        params = {self.SEND_MESSAGE:{plugin.ARGS:[discord.Object(id=discord_channel)], plugin.KWARGS:{'embed':embed.create_embed(description="A new reply has been made to <" + comment[0] + "> (direct link: <"+comment[1]+"> )", footer={"text":"Reddit", "icon_url":REDDIT_LOGO})}}}
                        q.put(params)
                        # q.put([url[:-len(".rss?sort=new")], "https://reddit.com"+comments[0][0]])
                time.sleep(SLOWDOWN)
            except:
                # Prevent a failed run from crashing the whole thread
                redditLog.warning("Scraping " + url + " failed. Either the page has changed or the page is unavailable (possibly due to rate limiting)...")
                # traceback.print_exc()
        self.data.save()
        redditLog.debug("Finished scraping run in "+ str(time.time() - mostrecentrunstart))


    def is_new_comment(self, url, page):
        '''(str) -> bool
        checks reddit.txt for whether the url is new or not'''
        #is_new = True
        return url.strip("\n") not in self.data.content[page][self.SEEN]
