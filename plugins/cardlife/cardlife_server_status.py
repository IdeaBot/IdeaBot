from libs import plugin, embed, dataloader
import discord, traceback, datetime, os
import requests

CHANNEL = 'channel'
MESSAGE = 'message'
OFFICIAL_SERVERS = 'official_server_data'
MESSAGES = 'messagesloc'

class Plugin(plugin.OnReadyPlugin):
    '''Displays pretty messages about the bot's status on the Idea Development Server

**Usage**
```@Idea add cardlife server status ```

For more information, do
```@Idea help cardlife_add_server_status``` '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.CHANNEL_ID = self.config[CHANNEL]
        self.MESSAGE_ID = self.config[MESSAGE]
        self.channel = discord.Object(id=self.CHANNEL_ID)
        self.message = discord.Object(id=self.MESSAGE_ID)
        self.message.channel = self.channel
        self.public_namespace.messages_file = dataloader.loadfile_safe(self.config[MESSAGES], load_as='json')
        if not isinstance(self.public_namespace.messages_file.content, dict):
            self.public_namespace.messages_file.content = dict()
        self.public_namespace.messages = self.public_namespace.messages_file.content
        self.official_servers_data = dataloader.loadfile_safe(self.config[OFFICIAL_SERVERS])
        if not isinstance(self.official_servers_data.content, dict):
            self.official_servers_data.content = dict()
        self.official_servers=self.official_servers_data.content

    async def action(self):
        try:
            # used to reset stuff while developing
            # (edit_message does weird stuff sometimes)
            # await self.edit_message(self.message, embed=embed.create_embed(description=''))
            try:
                # cardlife REST API queries
                # login to CardLife to get PublicId
                auth = requests.post("https://live-auth.cardlifegame.com/api/auth/authenticate", json={"EmailAddress":self.config["email"], "Password":self.config["password"]})
                auth_json = auth.json()
                # get information about all servers
                lobby = requests.post('https://live-lobby.cardlifegame.com/api/client/games', json={"PublicId":auth_json["PublicId"]})
                servers_json = lobby.json()

            except: # catch server errors
                # TODO: log failed server requests
                # print("Received invalid response from CardLife servers, skipping run...")
                return # skip run

            # create embed description
            title = "**__CardLife Online Servers__**"
            description = ''
            highest_playercount=0
            for item in servers_json['Games']:
                playercount = '%s/%s'%(item['CurrentPlayers'], item['MaxPlayers'])
                if len(playercount)>highest_playercount:
                    highest_playercount=len(playercount)

            # create online server list str
            online_official_servers = dict()
            for item in servers_json['Games']:
                if item['IsOfficial']:
                    online_official_servers[str(item['Id'])]=item['WorldName']
                if not item['HasPassword']:
                    # create single line to describe server
                    playercount = '%s/%s'%(item['CurrentPlayers'], item['MaxPlayers'])
                    spaces = highest_playercount-len(playercount)
                    description+='`'+(spaces*'.')+playercount+'`| '
                    description+=''+item['WorldName']+''+'\n'

            # create offline official server list
            offline_servers_str=''
            for id in self.official_servers:
                if id not in online_official_servers:
                    offline_servers_str+='**!** | '+self.official_servers[id]+'\n'
            for id in online_official_servers:
                self.official_servers[id]=online_official_servers[id] # update server names

            if offline_servers_str!='':
                description+='\n**__Offline__**\n'+offline_servers_str

            footer=dict()
            footer['text'] = '(Unofficial) CardLife API'
            footer['icon_url'] = None
            em = embed.create_embed(description=description, footer=footer, colour=0xddae60, title=title)
            for msg in self.public_namespace.messages:
                message = discord.Object(id=msg)
                message.channel = discord.Object(id=self.public_namespace.messages[msg])
                await self.edit_message(message, embed=em)
            self.official_servers_data.content=self.official_servers
            self.official_servers_data.save()
        except:
            traceback.print_exc()
            pass
    def shutdown(self):
        self.official_servers_data.content=self.official_servers
        self.official_servers_data.save()


def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size
