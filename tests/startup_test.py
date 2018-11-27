import unittest
import bot as botlib
from libs import testlib

class StartupTest(unittest.TestCase):

    ''' Test case to test a full startup of the bot
    This tests importing and initialization of all add-ons
    Everything up to (but not including) logging in to Discord is tested
    Shutdown is also tested to ensure that everything shutsdown properly
    (mainly threaded plugins that won't finish on their own)
    '''
    def test_startup(self):
        bot = botlib.Bot('./data/config.config', testlib.testlog)
        bot._shutdown()
