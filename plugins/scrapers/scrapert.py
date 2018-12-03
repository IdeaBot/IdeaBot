from bs4 import BeautifulSoup
from libs import dataloader, plugin, embed
import time, logging, discord, traceback, sys
from plugins.scrapers.scraperlibs import pageRet
import re

CHANNEL = 'channel'
CHANNELS = 'channels'
TWITTER_URL = r"https://twitter.com/openideaproject"
TWITTER_PROFILE_ICON = r"https://pbs.twimg.com/profile_images/913153081566691328/wDhS7B1w_400x400.jpg"
TWITTER_LOGO = r"https://pbs.twimg.com/profile_images/875087697177567232/Qfy0kRIP_400x400.jpg"
MOST_RECENT = 'most-recent'
MOST_RECENT2 = 'most-recent2'
FIRST = 'aaa-000'
RSS_URL_START = r'https://twitrss.me/twitter_user_to_rss/?user='

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

class Plugin(plugin.ThreadedPlugin):
    '''Multithreaded plugin for scraping Twitter through RSS

**Usage**
```@Idea (add or remove) <url> ```

Currently, this will scrape any valid twitter account given to it '''
    def __init__(self, **kwargs):
        super().__init__(should_spawn_thread=False, **kwargs)
        self.data = dataloader.loadfile_safe(self.config["datafilepath"])
        if not isinstance(self.data.content, dict):
            self.data.content = dict()
        # self.author = self.get_author_from_url(self.config["url"])
        # self.CHANNEL_ID = self.config[CHANNEL] # discord server channel ID for sending twitter updates to
        self.CHANNEL = CHANNEL
        self.CHANNELS = CHANNELS
        self.MOST_RECENT = MOST_RECENT
        self.MOST_RECENT2 = MOST_RECENT2
        self.FIRST = FIRST
        self.threaded_kwargs={'newTwit':self.public_namespace.newTwitterChannel}
        self.spawn_process()

    def threaded_action(self, q, newTwit=plugin.Queue(), **kwargs):
        '''(ThreadedPlugin, Queue ) -> None
        Checks continuously for new tweets from the official twitter.
        This should be run in a different thread since it is blocking (it's a while loop ffs)'''
        # handle new items from url_adder
        while not newTwit.empty():
            item = newTwit.get()
            item['url']=item['url'].strip('/').lower()
            if item["action"] == "remove" or item["action"] == "delete":
                try:
                    del(self.data.content[item["url"]][self.CHANNELS][self.data.content[item["url"]][self.CHANNELS].index(item[self.CHANNEL])])
                    if self.data.content[item["url"]][self.CHANNELS] == list():
                        del(self.data.content[item["url"]])
                except (TypeError, KeyError, ValueError, NameError):
                    # traceback.print_exc()
                    pass
            elif item["action"]=="add":
                twitLog.debug("Adding "+item['url'])
                if item["url"] not in self.data.content:
                    self.data.content[item["url"]]={self.CHANNELS:list(), self.MOST_RECENT:self.FIRST, self.MOST_RECENT2:self.FIRST} # dict
                self.data.content[item["url"]][self.CHANNELS].append(item[self.CHANNEL])
        # do scrape things
        for twitAccount in self.data.content: # twitAccount is the user's account URL
            twitLog.debug("Now scraping "+twitAccount)
            mostrecentrunstart = time.time()
            try:
                author = self.get_twitter_user_from_url(twitAccount)
                twitLog.debug("URL: "+RSS_URL_START+author)
                rss = BeautifulSoup(pageRet.pageRet(RSS_URL_START+author).decode(), "html.parser") # rss page
                items = rss.find_all("item")
                #print(items)
                tweets = [[self.get_url(x), self.get_tweet(x), x] for x in items] # create list of [url to tweet, tweet content]
                pinned_tweet = tweets[0]
                tweets = tweets[1:] # remove first tweet since it's pinned

                if len(tweets)>1 and self.is_new_tweet(tweets[0][0], twitAccount) and self.is_new_tweet(tweets[1][0], twitAccount, second=True):
                    if self.data.content[twitAccount][self.MOST_RECENT]==self.FIRST:
                        tweets=tweets[0:2]
                    for i in tweets:
                        if self.is_new_tweet(i[0], twitAccount):
                            twitLog.debug("New tweet found: " + i[0])
                            tweet_author = self.get_author(i[2])
                            tweet = {"url":i[0], "content":i[1], "author":tweet_author, "retweet":False}
                            # search for picture in content
                            img_link = self.get_image(i[2])
                            img=None
                            if img_link is not None: # set pic
                                img = {'url':img_link}
                                tweet['content']=tweet['content'].replace(img_link, '')
                                tweet['content']=re.sub(r'pic\.twitter\.com/([\w\d]+)', '', tweet['content'], re.I)
                            if author.lower() != tweet_author.lower():
                                tweet["retweet"] = True
                                em = embed.create_embed(image=img, author={"name":author+" retweeted "+tweet["author"], "url":tweet["url"], 'icon_url':None}, description=tweet["content"], footer={"text":"Twitter", "icon_url":TWITTER_LOGO})
                            else:
                                good_author=tweet["author"]
                                em = embed.create_embed(image=img, author={"name":good_author, "url":tweet["url"], 'icon_url':None}, description=tweet["content"], footer={"text":"Twitter", "icon_url":TWITTER_LOGO})
                            for discord_channel in self.data.content[twitAccount][self.CHANNELS]:
                                params= {self.SEND_MESSAGE:{plugin.ARGS:[discord.Object(id=discord_channel)], plugin.KWARGS:{'embed':em}}}
                                q.put(params)
                                #q.put(q_entry)
                        else:
                            break
                    # self.delete_entry("most recent tweet:")
                    if good_author!= author: # fix author capitalisation if necessary
                        good_twitAccount = twitAccount.replace(author, good_author)
                        self.data.content[good_twitAccount] = self.data.content[twitAccount]
                        self.data.content[twitAccount] = None
                        del(self.data.content[twitAccount])
                        twitAccount = good_twitAccount
                    self.data.content[twitAccount][self.MOST_RECENT]=tweets[0][0]
                    self.data.content[twitAccount][self.MOST_RECENT2]=tweets[1][0]
                    twitLog.debug("Most recent tweet is now: " + tweets[0][0])
                    twitLog.debug("Second most recent tweet is now: " + tweets[1][0])
                twitLog.debug("Finished scraping run in "+ str(time.time() - mostrecentrunstart))
            except:
                # Prevent a failed run from crashing the whole thread
                twitLog.warning("Scraping run failed. Either the page has changed or the page is unavailable...")
                traceback.print_exc()
        self.data.save()

    def get_tweet(self, bso):
        '''(BeautifulSoup object) -> str
        gets the text from title'''
        return bso.find("title").get_text()
    def get_url(self, bso):
        '''(BeautifulSoup object) -> str
        gets the text from guid'''
        return bso.find("guid").get_text()


    def is_new_tweet(self, url, twitAccount, second=False):
        '''(str [, bool]) -> bool
        returns True if the url is new, False otherwise'''
        is_new = True
        if url == self.data.content[twitAccount][self.MOST_RECENT] and not second:
            return False
        elif url == self.data.content[twitAccount][self.MOST_RECENT2]:
            return False
        else:
            return True
        '''
        if len(self.data.content) > 0:
            for i in range(len(self.data.content)):
                if self.data.content[i][:len("Most Recent Tweet:")].lower() == "most recent tweet:" and not second: # if it's the file line about most recent thread
                    if url == self.data.content[i][len("Most Recent Tweet:"):len("Most Recent Tweet:")+len(url)]:
                        is_new = False
                if self.data.content[i][:len("Second Most Recent Tweet:")].lower() == "second most recent tweet:" :
                    if url == self.data.content[i][len("Second Most Recent Tweet:"):len("Second Most Recent Tweet:")+len(url)]:
                        is_new = False
        return is_new'''

    def delete_entry(self, string):
        '''(str)->bool
        delete the first entry in self.data.content that contains string, if it exists'''
        for i in range(len(self.data.content)):
            if string.lower() in self.data.content[i].lower():
                del(self.data.content[i])
                return True
        return False

    def get_author(self, bso):
        '''(BeautifulSoup object) -> str
        find the author's twitter handle '''
        return bso.find("dc:creator").get_text().strip(" (@)")

    def get_author_from_url(self, url):
        '''(str) -> str
        find the author's twitter handle in the url'''
        return url.split("=")[-1].strip("/")

    def get_twitter_user_from_url(self, url):
        '''(str) -> str
        find the twitter handle for a user from their twitter url'''
        return url.strip('/').split('/')[-1]

    def get_image(self, bso):
        '''(BeautifulSoup object) -> str
        get the url link to the first image in the tweet (None if no image) '''
        desc = bso.find('description')
        img=re.search(r'\<\s*img\s+src\=\"(.+?)\"\s+width\=\"\d+\"\s+\/\>', str(desc), re.I)
        return img.group(1) if img is not None else None
