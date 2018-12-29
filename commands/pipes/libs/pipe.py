from libs import embed, dataloader
import discord

PIPE_SAVE_LOC = 'data/pipes.json'

class Pipe():
    # pipe behaviour mode constants
    ONEWAY = 'one-way'
    TWOWAY = 'two-way'
    THREEWAY = 'you-wish'

    # pipe message style constants
    DEFAULT = 'default-style'
    EMBED = 'embed-style'

    #pipe permissions constants
    PUBLIC = 'public'
    PRIVATE = 'private'

    def __init__(self, name, root_channel, channels=list(), mode=ONEWAY, style=DEFAULT, perm=PUBLIC, owner='', maintainers=list()):
        self.name = name
        self.root_channel = root_channel
        self.channels = list(channels)
        self.mode = mode
        self.style = style
        self.perm = perm
        self.owner = owner
        self.maintainers = list(maintainers)

    def dump(self):
        return {'name':self.name, 'root_channel':self.root_channel, 'channels':self.channels, 'mode':self.mode, 'style':self.style, 'perm':self.perm, 'owner':self.owner, 'maintainers':self.maintainers}

    def getOtherChannelIds(self, channel_id):
        if channel_id == self.root_channel:
            return self.channels
        all_channels = self.getAllChannels()
        all_channels.remove(channel_id)
        return all_channels

    def getAllChannels(self):
        return self.channels+[self.root_channel]

    def getAllStartChannels(self):
        if self.mode==self.ONEWAY:
            return [self.root_channel]
        else:
            return self.getAllChannels()

    def gen_message(self, message):
        if self.style==self.DEFAULT:
            return [message.content], {'embed':None}
        if self.style==self.EMBED:
            em = em = embed.create_embed(author={"name":message.author.display_name, "url":None, "icon_url":message.author.avatar_url},
                footer={"text": "#"+message.channel.name+" of "+message.server.name, "icon_url":None},
                description=message.content,
                colour=0xeeeeee)
            return [], {'embed':em}


def load_pipes():
    pipes = dataloader.loadfile_safe(PIPE_SAVE_LOC, load_as='json').content
    if not isinstance(pipes, list):
        pipes = list()
        return pipes
    for i in range(len(pipes)):
        pipes[i] = Pipe(**pipes[i])
    return pipes

def save_pipes(pipes):
    pipe_dump = list()
    for pipe in pipes:
        pipe_dump.append(pipe.dump())
    pipe_file = dataloader.loadfile_safe(PIPE_SAVE_LOC, load_as='json')
    pipe_file.content = pipe_dump
    pipe_file.save(save_as='json')
