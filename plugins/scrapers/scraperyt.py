from bs4 import BeautifulSoup
from libs import dataloader, plugin, embed
import requests, json, discord, traceback

'''
token="AIzaSyA8swoxzPs-cBK-Laxw3gAoH3ACBErmCfM" # Youtube API token, because security!
id="UCxVG9JnDocRPTiBMc_G04_w" # Idea Project
'''
URL = 'url'
CHANNEL = 'channel'
MESSAGE = 'message'

CHANNEL_URL='channel_url'
UPLOADS_URL='uploads_url'

class Plugin(plugin.ThreadedPlugin, plugin.OnReadyPlugin):
    def __init__(self, **kwargs):
        super().__init__(should_spawn_thread=False, **kwargs)
        self.data = dataloader.datafile(self.config["datafilepath"])
        self.CHANNEL_ID = self.config[CHANNEL]
        self.MESSAGE_ID = self.config[MESSAGE]
        self.CHANNEL_URL = self.config[CHANNEL_URL]
        self.UPLOADS_URL = self.config[UPLOADS_URL]
        self.spawn_process()

    def threaded_action(self, q):
        '''Keeps a message updated by editing the message periodically'''
        try:
            channel_info = json.loads(requests.get(self.CHANNEL_URL).text) # one liners ftw (API GET to self.URL is loaded as JSON)
            uploads_info = json.loads(requests.get(self.UPLOADS_URL).text)
            #print(info)
            description = ""
            print("Sub count", channel_info['items'][0]['statistics']['subscriberCount'])
            description += "Subscribers: %s \n" % channel_info['items'][0]['statistics']['subscriberCount']

            print("Video count", channel_info['items'][0]['statistics']['videoCount'])
            description += "Upload count: %s \n" % channel_info['items'][0]['statistics']['videoCount']

            print("Uploads", uploads_info['items'][0]['player']['embedHtml'])
            upload_iframe = uploads_info['items'][0]['player']['embedHtml']
            upload_url = upload_iframe.split('src=')[1].split(' ')[0].strip("\'\"").replace('embed/videoseries', 'playlist')
            print(upload_url)
            description += "Uploads: %s \n" % upload_url

            message = discord.Object(id=self.MESSAGE_ID)
            message.channel = discord.Object(id='471832405049606164')#self.CHANNEL_ID)
            # q.put({plugin.EDIT_MESSAGE:{plugin.ARGS:[message], plugin.KWARGS:{'embed':embed.create_embed(description=description)} } })
        except:
            traceback.print_exc()
