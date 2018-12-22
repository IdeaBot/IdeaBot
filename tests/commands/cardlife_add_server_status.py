from libs import testlib

test_messages=['add CardLife server status message {bot-mention}', '{bot-mention} create cl status']

class CardLifeTest(testlib.TestCase):
    def test_cardlife_add(self):
        self.assertIn('cardlife_add_server_status', self.bot.commands)
        cl = self.bot.commands['cardlife_add_server_status']
        for msg_content in test_messages:
            msg_content = msg_content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            msg = testlib.TestMessage(content=msg_content)
            self.assertTrue(cl._matches(msg), "Match failed for %s" % msg_content)
            self.assertIsNone(self.loop.run_until_complete(cl._action(msg)), "Action failed for %s" % msg_content)
            #NOTE: credentials for CardLife API are incorrect so response will not be an embed
            self.assertIsNotNone(self.bot.last_embed, "Missing embed for %s" %msg_content)
            self.bot.last_embed=None
