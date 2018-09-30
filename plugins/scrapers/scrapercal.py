from libs import plugin, embed, dataloader
import requests, datetime, traceback, json, discord

URL = 'url'
TOKEN = 'token'
CHANNEL = 'channel'
CALENDAR = 'calendarid'
GOOGLE_LOGO = 'http://www.google.com/favicon.ico' # yes, I didn't know this existed either
MAX_RESULTS = 4
DATE_MODE = 'readable' # 'readable' or 'default'

class Plugin(plugin.ThreadedPlugin):
    '''Multithreaded plugin for retrieving Google Calendar info

    Currently, cal only scrapes info from the Idea Project public calendar

    This uses Google API calls'''

    def __init__(self, **kwargs):
        super().__init__(should_spawn_thread=False, **kwargs)
        self.CHANNEL = discord.Object(id=self.config[CHANNEL])
        self.data = dataloader.loadfile_safe(self.config["datafilepath"]) # should be a txt file
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

    def threaded_action(self, q):
        try:
            calendar_id = 'igf697fg6c7kq902onikg35gi0@group.calendar.google.com' # Idea Project calendar id
            # calendar = requests.get(self.config[URL]+calendar_id+'?key='+self.config[TOKEN]) # doesn't work (Login required)
            events = requests.get(self.config[URL]+self.config[CALENDAR]+r'/events'+'?key='+self.config[TOKEN]+
            '&timeMin='+datetime.datetime.utcnow().isoformat()+'Z'+
            '&maxResults=%s' % MAX_RESULTS +
            '&singleEvents=True&orderBy=startTime')
            events = json.loads(events.text)
            items = events['items']
            for item in items:
                if item['id'] not in self.data.content:
                    self.data.content.append(item['id'])
                    description = '__**%s**__' % item['summary']
                    if 'dateTime' in item['start']:
                        datething = 'dateTime'
                    else:
                        datething = 'date'
                    description+='\n' + self.process_date(item['start'][datething]) + ' to ' + self.process_date(item['end'][datething]) + ' UTC\n'
                    cal_embed = embed.create_embed( description=description,
                    author={'name':'G-Cal', 'url':item['htmlLink'], 'icon_url':GOOGLE_LOGO},
                    footer={'text':item['organizer']['displayName'], 'icon_url':None} )
                    q.put({self.SEND_MESSAGE:{plugin.ARGS:[self.CHANNEL], plugin.KWARGS:{'embed':cal_embed}}})
            self.data.save()
        except:
            traceback.print_exc()
