from libs import plugin, embed, discordstats
import discord, traceback, datetime, os
import requests

CHANNEL = 'channel'
MESSAGE = 'message'

class Plugin(plugin.OnReadyPlugin):
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
        self.weird_restarts = -1
        self.stats_fileend = 0
        self.last_message_count = -1

    async def action(self):
        try:
            # used to reset stuff while developing
            # (edit_message does weird stuff sometimes)
            # await self.edit_message(self.message, embed=embed.create_embed(description=''))

            # cardlife REST API queries
            # login to CardLife to get PublicId
            auth = requests.post("https://live-auth.cardlifegame.com/api/auth/authenticate", json={"EmailAddress":self.config["email"], "Password":self.config["password"]})
            auth_json = auth.json()
            # get information about all servers
            lobby = requests.post('https://live-lobby.cardlifegame.com/api/client/games', json={"PublicId":auth_json["PublicId"]})
            servers_json = lobby.json()

            # create embed description
            title = "**__CardLife Online Servers__**"
            description = ''
            highest_playercount=0
            for item in servers_json['Games']:
                playercount = '%s/%s'%(item['CurrentPlayers'], item['MaxPlayers'])
                if len(playercount)>highest_playercount:
                    highest_playercount=len(playercount)

            for item in servers_json['Games']:
                if not item['HasPassword']:
                    # create single line to describe server
                    # info = (item['WorldName'],'|','%s/%s\n'%(item['CurrentPlayers'], item['MaxPlayers']))
                    #description+='{0[0]:<12}{0[1]:^12}{0[2]:>12}'.format(info) # formatting doens't work on Discord
                    '''if len(item['Region'])>2:
                        description+='`'+item['Region'].upper()+'|'
                    else:
                        description+=item['Region'].upper()+' |' '''

                    playercount = '%s/%s'%(item['CurrentPlayers'], item['MaxPlayers'])
                    spaces = highest_playercount-len(playercount)
                    description+='`'+(spaces*'.')+playercount+'`| '
                    description+=''+item['WorldName']+''+'\n'

            footer=dict()
            footer['text'] = '(Unofficial) CardLife API'
            footer['icon_url'] = None

            await self.edit_message(self.message, embed=embed.create_embed(description=description, footer=footer, colour=0xddae60, title=title))
        except:
            traceback.print_exc()
            pass
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
