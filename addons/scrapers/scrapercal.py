from libs import plugin, embed, dataloader
import requests, datetime, time, traceback, json, discord

URL = 'url'
TOKEN = 'token'
CHANNEL = 'channel'
CALENDAR = 'calendarid'
GOOGLE_LOGO = 'http://www.google.com/favicon.ico' # yes, I didn't know this existed either
MAX_RESULTS = 4
DATE_MODE = 'readable' # 'readable' or 'default'

SEEN = 'seen'
CHANNELS = 'channels'
CHANNEL = 'channel'

class Plugin(plugin.ThreadedPlugin):
    '''Multithreaded plugin for retrieving Google Calendar info

**Usage**
```@Idea (add or remove) <url> ```

Currently, this will scrape any valid calendar given to it

This uses Google API calls'''

    def __init__(self, **kwargs):
        super().__init__(should_spawn_thread=False, **kwargs)
        self.CHANNEL = CHANNEL
        self.data = dataloader.loadfile_safe(self.config["datafilepath"]) # should be a json file
        if not isinstance(self.data.content, dict):
            self.data.content = dict()
        self.SEEN = SEEN
        self.CHANNELS = CHANNELS
        self.threaded_kwargs = {"newGCal":self.public_namespace.newGCal}
        self.spawn_process()

    def process_date(self, date_str, mode=DATE_MODE):
        if mode=='default':
            return date_str.replace('T', ' ').strip('Z')
        elif mode=='readable':
            # NOTE: can be replaced by date_obj = datetime.datetime.fromisoformat(date_str) in Python3.7
            split_date_str = date_str.strip('Z').split('T')
            if len(split_date_str)==2:
                date, time = split_date_str
                year, month, day = date.split('-')
                hour, minute, second = time.split(':')
                date_obj = datetime.datetime( int(year), int(month), int(day), hour=int(hour), minute=int(minute) )
                return date_obj.ctime()
            elif len(split_date_str)==1:
                date = split_date_str[0]
                year, month, day = date.split('-')
                date_obj = datetime.datetime( int(year), int(month), int(day) )
                return date_obj.ctime()
            else:
                return date_str
        else:
            return date_str

    def threaded_action(self, q, newGCal=plugin.Queue()):
        # handle new items from url_adder
        while not newGCal.empty():
            item = newGCal.get()
            item["id"]=item["id"].split('%40group.calendar.google.com')[0]
            item["id"]=item["id"]+"@group.calendar.google.com"
            if item["action"] == "remove" or item["action"] == "delete":
                try:
                    del(self.data.content[item["id"]][self.CHANNELS][self.data.content[item["id"]][self.CHANNELS].index(item[self.CHANNEL])])
                except (TypeError, KeyError, ValueError, NameError):
                    # traceback.print_exc()
                    pass
            elif item["action"]=="add":
                if item["id"] not in self.data.content:
                    self.data.content[item["id"]]={self.CHANNELS:list(), self.SEEN:list()} # dict
                self.data.content[item["id"]][self.CHANNELS].append(item[self.CHANNEL])
        # do scrape things
        for calendar_id in self.data.content:
            try:
                url = (self.config[URL]+calendar_id+r'/events'+'?key='+self.config[TOKEN]+
                '&timeMin='+datetime.datetime.utcnow().isoformat()+'Z'+
                '&timeMax='+( datetime.datetime.utcnow()+datetime.timedelta(seconds=self.threaded_period) ).isoformat()+'Z'+
                '&maxResults=%s' % MAX_RESULTS +
                '&singleEvents=True&orderBy=startTime')
                # print(url)
                events = requests.get(url)
                events = json.loads(events.text)
                # print(json.dumps(events, indent=2))
                items = events['items']
                for item in items:
                    if item['id'] not in self.data.content[calendar_id][self.SEEN]:
                        self.data.content[calendar_id][self.SEEN].append(item['id'])
                        description = '__**%s**__' % item['summary']
                        if 'dateTime' in item['start']:
                            datething = 'dateTime'
                        else:
                            datething = 'date'
                        description+='\n' + self.process_date(item['start'][datething]) + ' to ' + self.process_date(item['end'][datething]) + ' UTC\n'
                        cal_embed = embed.create_embed( description=description,
                        author={'name':'Google Calendar (Upcoming)', 'url':item['htmlLink'], 'icon_url':GOOGLE_LOGO},
                        footer={'text':item['organizer']['displayName'], 'icon_url':None} )
                        for discord_channel in self.data.content[calendar_id][self.CHANNELS]:
                            q.put({self.SEND_MESSAGE:{plugin.ARGS:[discord.Object(id=discord_channel)], plugin.KWARGS:{'embed':cal_embed}}})
            except:
                # TODO: log request failure
                # print('Failed on %s' %calendar_id)
                # traceback.print_exc()
                pass
        self.data.save()
