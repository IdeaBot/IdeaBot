from libs import testlib
import re

test_messages = [r'{bot-mention} snark me up Scotty']

class SnarkTest(testlib.TestCase):
    '''Example test case for testing functionality of testlib as well as zz_invalid '''

    def test_snark(self):
        self.assertIn('snark', self.bot.commands)
        snark = self.bot.commands['snark']
        for msg_content in test_messages:
            msg_content = msg_content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            self.assertTrue(snark._matches(testlib.TestMessage(content=msg_content)))
            self.assertIsNone(self.loop.run_until_complete(snark._action(testlib.TestMessage())) )
        #self.assertEqual(self.bot.last_message, 'I\'m sorry, did you say `KILL ALL HUMANS`?')
