from libs import plugin, embed, discordstats
import discord, traceback, datetime, os

CHANNEL = 'channel'
MESSAGE = 'message'

class Plugin(plugin.OnReadyPlugin, plugin.AdminPlugin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.CHANNEL_ID = self.config[CHANNEL]
        self.MESSAGE_ID = self.config[MESSAGE]
        self.channel = discord.Object(id=self.CHANNEL_ID)
        self.message = discord.Object(id=self.MESSAGE_ID)
        self.message.channel = self.channel
        self.startup_time = datetime.datetime.now()
        self.weird_restarts = -1
        self.stats_fileend = 0
        self.last_message_count = -1

    async def action(self):
        try:
            # used to reset stuff while developing
            # (edit_message does weird stuff sometimes)
            # await self.edit_message(self.message, embed=embed.create_embed(description=''))

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

            description += "**Last saved stats file** : %s \n" % self.stats_fileend
            description += "**Uptime** : %s \n" % str(datetime.datetime.now()-self.startup_time).split('.')[0] # uptime, without decimal seconds
            description +="**Weird Restarts** : %s \n" % self.weird_restarts
            description += "**Idea Size** : %s bytes \n" % get_size()
            description += "***Last Updated** : %s* \n" % datetime.datetime.now().isoformat()
            # description += "~~Potatoes picked~~ : 2\n"

            # create embed author
            author=dict()
            author['name'] = self.bot.user.name if self.bot.user.name!=None else None
            author['icon_url'] = self.bot.user.avatar_url
            author['url'] = r'https://github.com/NGnius/IdeaBot' # Remove if perceived as advertising

            await self.edit_message(self.message, embed=embed.create_embed(description=description, author=author))

            if self.last_message_count>len(self.bot.messages) or self.last_message_count==-1: # detect partial bot restarts
                self.stats_fileend = self.startup_time.isoformat() # change filename to not save over last file
                self.weird_restarts += 1
            discordstats.dumpMessages(self.bot, filename='./data/msgdump%s.csv' % self.stats_fileend)
            self.last_message_count = len(self.bot.messages)
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
