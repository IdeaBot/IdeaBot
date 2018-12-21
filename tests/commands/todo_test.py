from libs import testlib

test_add_messages = ['{bot-mention} todo add we are number 1 to Test List', '{bot-mention} todo make a stew', '{bot-mention} todo add My life']
test_list_messages = ['{bot-mention} todo', '{bot-mention} todo list for Test List']
test_rm_messages = ['{bot-mention} todo reMove My life', '{bot-mention} todo finish make a stew ', '{bot-mention} todo complete we are number 1 from Test List']

class ToDoTest(testlib.TestCase):
    def setUp(self):
        super().setUp()
        self.todo_cmd = self.bot.commands['todo']

    def test_todo(self):
        # test adding
        # print("Adding...")
        for msg_content in test_add_messages:
            msg_content = msg_content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            msg = testlib.TestMessage(content=msg_content)
            self.assertTrue(self.todo_cmd._matches(msg), "Match failed for %s " % msg_content)
            self.assertIsNone(self.loop.run_until_complete(self.todo_cmd._action(msg)), "Action failed for %s " % msg_content)
            self.assertIsNotNone(self.bot.last_embed, "Missing embed")
            self.bot.last_embed=None

        # test listing
        # print("Listing...")
        for msg_content in test_list_messages:
            msg_content = msg_content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            msg = testlib.TestMessage(content=msg_content)
            self.assertTrue(self.todo_cmd._matches(msg), "Match failed for %s " % msg_content)
            self.assertIsNone(self.loop.run_until_complete(self.todo_cmd._action(msg)), "Action failed for %s " % msg_content)
            self.assertIsNotNone(self.bot.last_embed, "Missing embed")
            self.bot.last_embed=None

        # test removing
        # print("Removing...")
        for msg_content in test_rm_messages:
            msg_content = msg_content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            msg = testlib.TestMessage(content=msg_content)
            self.assertTrue(self.todo_cmd._matches(msg), "Match failed for %s " % msg_content)
            self.assertIsNone(self.loop.run_until_complete(self.todo_cmd._action(msg)), "Action failed for %s " % msg_content)
            self.assertIsNotNone(self.bot.last_embed, "Missing embed")
            # print(self.bot.last_embed)
            self.bot.last_embed=None
