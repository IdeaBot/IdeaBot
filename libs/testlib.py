'''
A collection of fake stuff to automate testing without Discord.

This is NOT fully featured, and many testing errors can be caused by this lib.
The advantage comes in the form of automation and speed, since most
calls to discord.py functions/methods are emulated by testlib.
Testlib also doesn't need internet access, which is great for offline testing.

@author: NGnius
'''

import bot
import asyncio, logging, discord
import unittest

import collections

def testLogging():
    '''() -> Logger class
    set ups main log so that it outputs to ./test.log and then returns the log'''
    logger = logging.getLogger('test')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='tests/test.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
    logger.addHandler(handler)
    return logger

testlog=testLogging()

ADD = 'add'
REMOVE='remove'

class TestBot(bot.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, log=testlog, **kwargs)
        self.user=TestUser(user_id='9'*18)
        self.message_history=collections.deque(maxlen=64)
        self.reaction_history=collections.deque(maxlen=64)
        self.last_message = None
        self.last_edit_message = None
        self.last_reaction_message = None
        self.last_embed = None
        self.last_destination = None
        self.last_reaction_emoji = None

    #TODO: make assert methods that check the inputs to these methods
    @asyncio.coroutine
    def send_message(self, destination, content=None, *args, tts=False, embed=None):
        message = TestMessage(channel=destination, content=content, embed=embed)
        self.last_message = content
        self.last_embed = embed
        self.last_destination = destination
        self.message_history.append(message)
        return message

    @asyncio.coroutine
    def edit_message(self, message, new_content=None, *args, embed=None):
        self.last_message = content
        self.last_destination = destination
        self.last_edit_message = message
        self.last_message = new_content
        self.last_embed = embed
        message.content = new_content
        return message

    @asyncio.coroutine
    def add_reaction(self, message, emoji):
        reaction = TestReaction(emoji=emoji, message=message)
        self.last_reaction_emoji=emoji
        self.last_reaction_message = message
        self.last_reaction_action=ADD
        self.reaction_history.append(reaction)
        return reaction

    @asyncio.coroutine
    def remove_reaction(self, message, emoji, member):
        reaction = TestReaction(emoji=emoji, message=message)
        self.last_reaction_emoji=emoji
        self.last_reaction_message = message
        self.last_reaction_action=REMOVE
        self.reaction_history.append(reaction)
        return reaction

    @asyncio.coroutine
    def send_typing(self,destination):
        self.last_destination = destination

    @asyncio.coroutine
    def send_file(self, destination, fp, **kwargs):
        self.last_destination = destination
        self.last_file = fp

    def load_messages(self):
        return

    @asyncio.coroutine
    def get_user_info(*args):
        return TestUser()

class TestUser(discord.User):
    def __init__(self, user_id='0'*18, name='test'):
        self.id=user_id
        self.name=name
        #self.mention='<@!'+user_id+'>'

class TestServer(discord.Server):
    def __init__(self, server_id='0'*18, me=TestUser(user_id='9'*18)):
        self.id=server_id
        self.me=me

class TestMember(discord.Member):
    def __init__(self, user_id='0'*18, server=TestServer()):
        self.id=user_id
        self.server=server
        #self.mention='<@!'+user_id+'>'

class TestChannel(discord.Channel):
    def __init__(self, channel_id='0'*18, server=TestServer()):
        self.id=channel_id
        self.server=server

class TestMessage(discord.Message):
    def __init__(self, content='', message_id='0'*18, channel=TestChannel(), author=TestMember(), server=TestServer(), embed=None):
        self.id=message_id
        self.channel=channel
        self.author=author
        self.content=content
        self.server=server
        self.embed=embed

class TestEmoji(discord.Emoji):
    def __init__(self, name='test', emoji_id='0'*18, server=TestServer(), url='https://www.google.com/favicon.ico'):
        self.name=name
        self.id=emoji_id
        self.server=server
        #self.url=url

class TestReaction(discord.Reaction):
    def __init__(self, emoji=TestEmoji(), message=TestMessage(), count=1):
        self.message=message
        self.emoji=emoji
        self.custom_emoji=isinstance(emoji, str)
        self.me=False
        self.count=count

import asyncio
class TestCase(unittest.TestCase):
    def setUp(self):
        self.bot = TestBot('./data/config.config')
        self.loop = asyncio.get_event_loop()
    def tearDown(self):
        self.bot._shutdown()
