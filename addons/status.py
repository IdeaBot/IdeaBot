from libs import plugin, embed, discordstats
import discord, traceback, datetime, os, time

CHANNEL = 'channel'
MESSAGE = 'message'

running = False
weird_restarts = 0

class Plugin(plugin.OnReadyPlugin, plugin.AdminPlugin):
    ''''Displays pretty messages about the bot's status on the Idea Development Server

**Usage**
```NONE``` '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.CHANNEL_ID = self.config[CHANNEL]
        self.MESSAGE_ID = self.config[MESSAGE]
        self.channel = discord.Object(id=self.CHANNEL_ID)
        self.message = discord.Object(id=self.MESSAGE_ID)
        self.message.channel = self.channel
        self.startup_time = datetime.datetime.now()
        self.startup_time_seconds = None

    async def action(self):
        try:
            # used to reset stuff while developing
            # (edit_message does weird stuff sometimes)
            # await self.edit_message(self.message, embed=embed.create_embed(description=''))
            if not self.startup_time_seconds:
                self.startup_time_seconds = time.perf_counter()

            # create embed description
            description = ""
            description += "**Servers** : %s \n" %len(self.bot.servers)
            description += "**Messages seen** : %s \n" %len(self.bot.messages)
            description += "**Messages watched** : %s \n" %len(self.bot.always_watch_messages)
            description += "**Users** : %s \n" % discordstats.total_users(self.bot)

            description += " - - - - - - - - - - - - - - - - - - - - - - \n" # seperator

            description += "**Plugins** : %s \n" % len(self.bot.plugins)
            description += "**Commands** : %s \n" % len(self.bot.commands)
            description += "**Reactions** : %s \n" % len(self.bot.reactions)

            description += " - - - - - - - - - - - - - - - - - - - - - - \n" # seperator

            description += "**Startup** : %s \n" % self.startup_time.isoformat()
            description += "**Uptime** : %s \n" % str(datetime.datetime.now()-self.startup_time).split('.')[0] # uptime, without decimal seconds
            description += "**Time Leak** : %.8fs  \n" % ( (time.perf_counter() - self.startup_time_seconds)%self.period ) # time leak since startup
            description += "**Idea Size** : %4.2f kB \n" % (get_size()/1024)
            description += "***Last Updated*** *: %s* \n" % datetime.datetime.now().isoformat()

            # create embed author
            author=dict()
            author['name'] = self.bot.user.name if self.bot.user.name!=None else None
            author['icon_url'] = self.bot.user.avatar_url
            author['url'] = r'https://github.com/NGnius/IdeaBot' # Remove if perceived as advertising

            await self.edit_message(self.message, embed=embed.create_embed(description=description, author=author))

            discordstats.dumpMessages(self.bot, filename='./data/msgdump%s.csv' % self.startup_time.isoformat())
        except:
            traceback.print_exc()
    '''
    def shutdown(self): # in order for this to work, shutdown has to be called before the bot terminates it's API connection, which is currently not the case
        yield from self.edit_message(self.message, new_content=' ', embed=embed.create_embed(description="Offline"))'''


def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size
