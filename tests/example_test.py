from libs import testlib

class ExampleTest(testlib.TestCase):
    '''Example test case for testing functionality of testlib as well as zz_invalid '''

    def test_example(self):
        self.assertIn('zz_invalid', self.bot.commands)
        zz_invalid = self.bot.commands['zz_invalid']
        # matches() should always evaluate to true for zz_invalid when the bot is mentioned
        self.assertTrue(zz_invalid._matches(testlib.TestMessage(content='<@!'+self.bot.user.id+'> ')))

        self.assertIsNone(self.loop.run_until_complete(zz_invalid._action(testlib.TestMessage())) )
        self.assertEqual(self.bot.last_message, 'I\'m sorry, did you say `KILL ALL HUMANS`?')
