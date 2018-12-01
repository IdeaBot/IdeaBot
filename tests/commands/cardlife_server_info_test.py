from libs import testlib

test_messages = [r'{bot-mention} server info "EU-PVE-Official-CardLife-01"', r'{bot-mention} server info "100001"']

#NOTE: These tests take a long time since they query the CardLife API via the Internet

class CardLifeTest(testlib.TestCase):
    def test_cardlife_info(self):
        self.assertIn('cardlife_server_info', self.bot.commands)
        cl = self.bot.commands['cardlife_server_info']
        for msg_content in test_messages:
            msg_content = msg_content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            msg = testlib.TestMessage(content=msg_content)
            self.assertTrue(cl._matches(msg), "Match failed")
            self.assertIsNone(self.loop.run_until_complete(cl._action(msg)), "Action failed")
            self.assertIsNotNone(self.bot.last_embed, "Missing embed")
            self.bot.last_embed=None
