from libs import testlib

test_messages = [r'{bot-mention} help {command} -c']

#NOTE: These tests take a long time since they query the CardLife API via the Internet

class HelpTest(testlib.TestCase):
    def test_help(self):
        self.assertIn('help', self.bot.commands)
        help_cmd = self.bot.commands['help']
        for msg_content in test_messages:
            msg_content = msg_content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            for cmd in self.bot.commands:
                msg_str = msg_content.replace('{command}', cmd)
                msg = testlib.TestMessage(content=msg_str)
                self.assertTrue(help_cmd._matches(msg), "Match failed")
                self.assertIsNone(self.loop.run_until_complete(help_cmd._action(msg, self.bot)), "Action failed")
                self.assertIsNotNone(self.bot.last_embed, "Missing embed")
                self.bot.last_embed=None
