from bs4 import BeautifulSoup
from libs import dataloader, plugin, embed
import requests, json, discord, traceback, math

URL = 'url'
CHANNEL = 'channel'
CHANNELS = 'channels'

CHANNEL_URL='channel_url'
UPLOADS_URL='uploads_url'
UPLOADS_ITEM_URL='upload_items_url'
VIDEO_URL_START='video_url_start'
CHANNEL_URL_START='channel_url_start'

# constants for data file (.json)
SUB_MILESTONE = 'submilestone'
UPLOAD_COUNT = 'uploads'

YOUTUBE_LOGO = 'https://s.ytimg.com/yts/img/favicon_144-vfliLAfaB.png'


class Plugin(plugin.ThreadedPlugin, plugin.OnReadyPlugin):
    '''Multithreaded plugin for YouTube channel information gathering

**Usage**
```@Idea (add or remove) <url> ```

Currently, this will scrape any valid YouTube channel given to it

This uses Google API calls '''
    def __init__(self, **kwargs):
        super().__init__(should_spawn_thread=False, **kwargs)
        self.data = dataloader.loadfile_safe(self.config["datafilepath"]) # should be a JSON file
        # make sure it is dict
        if not isinstance(self.data.content, dict):
            self.data.content = dict()
        self.CHANNEL_URL = self.config[CHANNEL_URL]
        self.UPLOADS_URL = self.config[UPLOADS_URL]
        self.UPLOADS_ITEM_URL = self.config[UPLOADS_ITEM_URL]
        self.VIDEO_URL_START = self.config[VIDEO_URL_START]
        self.CHANNEL_URL_START = self.config[CHANNEL_URL_START]
        self.CHANNELS = CHANNELS
        self.CHANNEL = CHANNEL
        self.threaded_kwargs = {"newChannel":self.public_namespace.newYTChannel}
        self.spawn_process()

    def is_new_milestone(self, sub_count, channel_id):
        '''(scraperyt Plugin, int or float or str) -> bool
        Determines if last milestone is an integer number lower than new milestone (n)
        A milestone is when n goes up an integer in Subscribers=10^n (ie n=log(Subscribers, 10) )

        Returns true if math.floor(old milestone) < math.floor(new milestone)'''

        # setup vars
        if channel_id in self.data.content and SUB_MILESTONE in self.data.content[channel_id]:
            old_milestone = math.floor(int(float(self.data.content[channel_id][SUB_MILESTONE])))
        else:
            old_milestone = -1
        new_milestone = math.floor(math.log(int(float(sub_count)), 10)) # accept any sort of number for sub_count
        # ^^^ is the log (base 10) of sub_count

        # logic
        if new_milestone>old_milestone:
            if channel_id not in self.data.content:
                self.data.content[channel_id] = dict()
            self.data.content[channel_id][SUB_MILESTONE] = new_milestone
            self.data.save()
            return True
        else:
            return False

    def get_new_milestone(self, channel_dict, channel_id):
        '''(scraperyt Plugin, dict) -> discord.Embed
        Generates an embed about the subscriber milestone from channel info'''

        channel = channel_dict['items'][0]
        message = channel['snippet']['title']+" has reached %s subscribers!" % 10**self.data.content[channel_id][SUB_MILESTONE]
        footer = {'text':channel['snippet']['title']} # unused
        author = {'name':channel['snippet']['title'], 'url':self.CHANNEL_URL_START+channel['id'], 'icon_url':YOUTUBE_LOGO}
        image = {'url':channel['snippet']['thumbnails']['default']['url']}
        return embed.create_embed(description=message, author=author, image=image)

    def new_upload(self, upload_count, channel_id):
        '''(scraperyt Plugin, int of float or str) -> bool
        returns True if upload_count > old_upload_count; False otherwise
        IKR - amazingly complex function!'''

        # setup vars
        new_upload_count = int(float(upload_count)) # accept any sort of number
        if UPLOAD_COUNT in self.data.content[channel_id]:
            old_upload_count = int(float(self.data.content[channel_id][UPLOAD_COUNT])) # accept any sort of number
        else:
            self.data.content[channel_id][UPLOAD_COUNT]=new_upload_count
            self.data.save()
            return True

        # logic
        if new_upload_count>old_upload_count:
            if channel_id not in self.data.content:
                self.data.content[channel_id] = dict()
            self.data.content[channel_id][UPLOAD_COUNT] = new_upload_count
            self.data.save()
            return True
        else:
            return False

    def get_new_upload(self, uploads_id):
        '''(scraperyt Plugin, dict) -> discord.Embed
        Generates an embed about the newest upload from channel info'''

        upload_items = json.loads(requests.get(self.UPLOADS_ITEM_URL+uploads_id).text)
        newest_upload = upload_items['items'][0]
        title = newest_upload['snippet']['title']
        description = newest_upload['snippet']['description'].split('\n')[0]
        image = {'url':newest_upload['snippet']['thumbnails']['maxres']['url']}
        author = {'name':title, 'url':self.VIDEO_URL_START+newest_upload['snippet']['resourceId']['videoId'], 'icon_url':YOUTUBE_LOGO}
        footer = {'text':newest_upload['snippet']['channelTitle'], 'icon_url':None}
        return embed.create_embed(description=description, image=image, author=author, footer=footer)

    def threaded_action(self, q, newChannel=plugin.Queue() ):
        '''Keeps a channel updated by sending messages about changes in YT channels periodically'''
        '''This should
        - send a message for logarithmic (exponential?) milestones (when n goes up an integer in Subscribers=10^n)
        - send a message for new videos
        - ???
        '''
        # handle new items from url_adder
        while not newChannel.empty():
            item = newChannel.get()
            if item["action"] == "remove" or item["action"] == "delete":
                try:
                    del(self.data.content[item["id"]][self.CHANNELS][self.data.content[item["id"]][self.CHANNELS].index(item[self.CHANNEL])])
                    if self.data.content[item["id"]][self.CHANNELS] == list():
                        del(self.data.content[item["id"]])
                except (TypeError, KeyError, ValueError, NameError):
                    # traceback.print_exc()
                    pass
            elif item["action"]=="add":
                if item["id"] not in self.data.content:
                    self.data.content[item["id"]]={self.CHANNELS:list()} # dict
                self.data.content[item["id"]][self.CHANNELS].append(item[self.CHANNEL])
        # do scrape things
        for channel_id in self.data.content:
            try:
                channel_info = json.loads(requests.get(self.CHANNEL_URL+channel_id).text) # one liners ftw (API GET to URL is loaded as JSON)
                uploads_id=channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                uploads_info = json.loads(requests.get(self.UPLOADS_URL+uploads_id).text)

                # get uploads playlist url
                upload_iframe = uploads_info['items'][0]['player']['embedHtml']
                upload_url = upload_iframe.split('src=')[1].split(' ')[0].strip("\'\"").replace('embed/videoseries', 'playlist')

                # sub milestone check
                subscriberCount = channel_info['items'][0]['statistics']['subscriberCount']
                if self.is_new_milestone(subscriberCount, channel_id):
                    for discord_channel in self.data.content[channel_id][self.CHANNELS]:
                        q.put({self.SEND_MESSAGE:{plugin.ARGS:[discord.Object(id=discord_channel)], plugin.KWARGS:{'embed': self.get_new_milestone(channel_info, channel_id) }}})

                # new upload check
                videoCount = channel_info['items'][0]['statistics']['videoCount']
                if self.new_upload(videoCount, channel_id):
                    # message = "IdeaProject has uploaded a new video! Go check it out here: %s" % upload_url
                    for discord_channel in self.data.content[channel_id][self.CHANNELS]:
                        q.put({self.SEND_MESSAGE:{plugin.ARGS:[discord.Object(id=discord_channel)], plugin.KWARGS:{'embed': self.get_new_upload(uploads_id) }}})

            except:
                print('Failed to scrape YT API for channel %s ' % channel_id)
                # traceback.print_exc()
