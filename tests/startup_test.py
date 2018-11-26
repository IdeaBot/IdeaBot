import unittest
import bot as botlib
import main

class TestTest(unittest.TestCase):

    ''' Test case to test a full startup of the bot
    This tests importing and initialization of all add-ons
    Everything up to (but not including) logging in to Discord is tested
    Shutdown is also tested to ensure that everything shutsdown properly
    (mainly threaded plugins that won't finish on their own)
    '''
    def test_startup(self):
        log = main.mainLogging()
        bot = botlib.Bot('./data/config.config', log)
        bot._shutdown()
