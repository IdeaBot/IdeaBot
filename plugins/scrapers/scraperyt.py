from bs4 import BeautifulSoup
from libs import dataloader, plugin, embed
import requests, json, discord, traceback, math

URL = 'url'
CHANNEL = 'channel'

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

    Currently, yt only scrapes the Idea Project YouTube channel

    This uses Google API calls '''
    def __init__(self, **kwargs):
        super().__init__(should_spawn_thread=False, **kwargs)
        self.data = dataloader.loadfile_safe(self.config["datafilepath"]) # should be a JSON file
        # make sure it is dict
        if not isinstance(self.data.content, dict):
            self.data.content = dict()
        self.CHANNEL_ID = self.config[CHANNEL]
        self.CHANNEL_URL = self.config[CHANNEL_URL]
        self.UPLOADS_URL = self.config[UPLOADS_URL]
        self.UPLOADS_ITEM_URL = self.config[UPLOADS_ITEM_URL]
        self.VIDEO_URL_START = self.config[VIDEO_URL_START]
        self.CHANNEL_URL_START = self.config[CHANNEL_URL_START]
        self.CHANNEL = discord.Object(id=self.CHANNEL_ID) # essentially a discord.Channel object
        self.spawn_process()

    def is_new_milestone(self, sub_count):
        '''(scraperyt Plugin, int or float or str) -> bool
        Determines if last milestone is an integer number lower than new milestone (n)
        A milestone is when n goes up an integer in Subscribers=10^n (ie n=log(Subscribers, 10) )

        Returns true if math.floor(old milestone) < math.floor(new milestone)'''

        # setup vars
        if SUB_MILESTONE in self.data.content:
            old_milestone = math.floor(int(float(self.data.content[SUB_MILESTONE])))
        else:
            old_milestone = -1
        new_milestone = math.floor(math.log(int(float(sub_count)), 10)) # accept any sort of number for sub_count
        # ^^^ is the log (base 10) of sub_count

        # logic
        if new_milestone>old_milestone:
            self.data.content[SUB_MILESTONE] = new_milestone
            self.data.save()
            return True
        else:
            return False

    def get_new_milestone(self, channel_dict):
        '''(scraperyt Plugin, dict) -> discord.Embed
        Generates an embed about the subscriber milestone from channel info'''

        channel = channel_dict['items'][0]
        message = channel['snippet']['title']+" has reached %s subscribers!" % 10**self.data.content[SUB_MILESTONE]
        footer = {'text':channel['snippet']['title']} # unused
        author = {'name':channel['snippet']['title'], 'url':self.CHANNEL_URL_START+channel['id'], 'icon_url':YOUTUBE_LOGO}
        image = {'url':channel['snippet']['thumbnails']['default']['url']}
        return embed.create_embed(description=message, author=author, image=image)

    def new_upload(self, upload_count):
        '''(scraperyt Plugin, int of float or str) -> bool
        returns True if upload_count > old_upload_count; False otherwise
        IKR - amazingly complex function!'''

        # setup vars
        if UPLOAD_COUNT in self.data.content:
            old_upload_count = int(float(self.data.content[UPLOAD_COUNT])) # accept any sort of number
        else:
            old_upload_count = -1
        new_upload_count = int(float(upload_count)) # accept any sort of number

        # logic
        if new_upload_count>old_upload_count:
            self.data.content[UPLOAD_COUNT] = new_upload_count
            self.data.save()
            return True
        else:
            return False

    def get_new_upload(self):
        '''(scraperyt Plugin, dict) -> discord.Embed
        Generates an embed about the newest upload from channel info'''

        upload_items = json.loads(requests.get(self.UPLOADS_ITEM_URL).text)
        newest_upload = upload_items['items'][0]
        title = newest_upload['snippet']['title']
        description = newest_upload['snippet']['description'].split('\n')[0]
        image = {'url':newest_upload['snippet']['thumbnails']['maxres']['url']}
        author = {'name':title, 'url':self.VIDEO_URL_START+newest_upload['snippet']['resourceId']['videoId'], 'icon_url':YOUTUBE_LOGO}
        footer = {'text':newest_upload['snippet']['channelTitle'], 'icon_url':None}
        return embed.create_embed(description=description, image=image, author=author, footer=footer)

    def threaded_action(self, q):
        '''Keeps a message updated by editing the message periodically'''
        '''This should
        - send a message for logarithmic (exponential?) milestones (when n goes up an integer in Subscribers=10^n)
        - send a message for new videos
        - ???
        '''
        try:
            channel_info = json.loads(requests.get(self.CHANNEL_URL).text) # one liners ftw (API GET to URL is loaded as JSON)
            uploads_info = json.loads(requests.get(self.UPLOADS_URL).text)

            # get uploads playlist url
            upload_iframe = uploads_info['items'][0]['player']['embedHtml']
            upload_url = upload_iframe.split('src=')[1].split(' ')[0].strip("\'\"").replace('embed/videoseries', 'playlist')

            # sub milestone check
            subscriberCount = channel_info['items'][0]['statistics']['subscriberCount']
            if self.is_new_milestone(subscriberCount):
                q.put({plugin.SEND_MESSAGE:{plugin.ARGS:[self.CHANNEL], plugin.KWARGS:{'embed': self.get_new_milestone(channel_info) }}})

            # new upload check
            videoCount = channel_info['items'][0]['statistics']['videoCount']
            if self.new_upload(videoCount):
                message = "IdeaProject has uploaded a new video! Go check it out here: %s" % upload_url
                q.put({plugin.SEND_MESSAGE:{plugin.ARGS:[self.CHANNEL], plugin.KWARGS:{'embed': self.get_new_upload() }}})

        except:
            traceback.print_exc()
