from libs import testlib

test_messages = [r'{bot-mention} help {command} -c']
list_messages = ['{bot-mention} help commands', '{bot-mention} help reActions', '{bot-mention} help plugin']

#NOTE: These tests take a long time since they query the CardLife API via the Internet

class HelpTest(testlib.TestCase):
    def setUp(self):
        super().setUp()
        self.help_cmd = self.bot.commands['help']

    def test_help(self):
        for msg_content in test_messages:
            msg_content = msg_content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            for cmd in self.bot.commands:
                msg_str = msg_content.replace('{command}', cmd)
                msg = testlib.TestMessage(content=msg_str)
                self.assertTrue(self.help_cmd._matches(msg), "Match failed for %s" %msg_str)
                self.assertIsNone(self.loop.run_until_complete(self.help_cmd._action(msg, self.bot)), "Action failed for %s" %msg_str)
                self.assertIsNotNone(self.bot.last_embed, "Missing embed for %s" %msg_str)
                self.bot.last_embed=None

    def test_list(self):
        for msg_content in list_messages:
            msg_content = msg_content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            #print(msg_content)
            msg = testlib.TestMessage(content=msg_content)
            self.assertTrue(self.help_cmd._matches(msg), "Match failed for %s" %msg_content)
            self.assertIsNone(self.loop.run_until_complete(self.help_cmd._action(msg, self.bot)), "Action failed for %s" %msg_content)
            self.assertIsNotNone(self.bot.last_embed, "Missing embed for %s" %msg_content)
            #print(self.bot.last_embed.description)
            self.bot.last_embed=None
