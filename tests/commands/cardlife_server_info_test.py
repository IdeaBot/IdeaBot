from libs import testlib

test_messages = [r'{bot-mention} cl server info "EU-PVE-Official-CardLife-01"', r'{bot-mention} cardlife server info "100001"']

#NOTE: These tests take a long time since they query the CardLife API via the Internet

class CardLifeTest(testlib.TestCase):
    def test_cardlife_info(self):
        self.assertIn('cardlife_server_info', self.bot.commands)
        cl = self.bot.commands['cardlife_server_info']
        for msg_content in test_messages:
            msg_content = msg_content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            msg = testlib.TestMessage(content=msg_content)
            self.assertTrue(cl._matches(msg), "Match failed for %s" % msg_content)
            self.loop.run_until_complete(cl._action(msg))
            #NOTE: credentials for CardLife API are incorrect so response will not be an embed
            self.assertGreaterEqual(len(self.bot.message_history), 1, "Missing message for %s" %msg_content)
            last_msg = self.bot.message_history.pop()
            self.assertIsNotNone(last_msg.content or last_msg.embed, "Missing message for %s" %msg_content)
            self.bot.last_message=None
