from libs import testlib
from addons.pipes.libs import pipe as pipe_class

create_messages = ['{bot-mention} plumb private pipe "Yo mama"', '{bot-mention} create private pipe Yo', '{bot-mention} create pipe "42"']
authorize_messages = ['{bot-mention} authorize {maintainer-mention} for pipe "test pipe"']
modify_messages = ['{bot-mention} add this to pipe "test pipe"', '{bot-mention} add {channel-mention} to pipe "test pipe"', '{bot-mention} add to pipe "test pipe"']
piper_messages = ['Yo wassup my homey-g']
delete_messages = ['{bot-mention} delete pipe "test pipe"', 'laaadeeeedaaaa potates are cool delete pipe "test pipe" yo mama is evil {bot-mention}']

root_id = '1'*18
dest_id = '2'*18

class PipesTest(testlib.TestCase):
    def setUp(self):
        super().setUp()
        self.pipe_create = self.bot.commands['pipe_create']
        self.pipe_authorize = self.bot.commands['pipe_authorize']
        self.pipe_modify = self.bot.commands['pipe_modify']
        self.pipe_delete = self.bot.commands['pipe_delete']
        self.piper = self.bot.commands['piper']
        self.piper.public_namespace.pipes = list()

    def test_create(self):
        channel = testlib.TestChannel(channel_id=root_id)
        for content in create_messages:
            content = content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            msg = testlib.TestMessage(content=content, channel=channel)
            self.assertTrue(self.pipe_create.matches(msg),'Match failed for %s' %content)
            self.loop.run_until_complete(self.pipe_create._action(msg))
            self.assertNotEqual(self.piper.public_namespace.pipes, list())
            test_pipe = find_pipe_by_root(root_id, self.piper.public_namespace.pipes)
            self.assertIsNotNone(test_pipe, 'Piped message not found for %s, id=%s' %(content, msg.channel.id) )
            # print(test_pipe.name)
            # remove test pipe
            self.piper.public_namespace.pipes.remove(test_pipe)

    def test_piper(self):
        # set up pipe
        test_pipe = pipe_class.Pipe(name='test pipe', root_channel=root_id, channels=[dest_id])
        self.piper.public_namespace.pipes.append(test_pipe)
        # test piper
        channel = testlib.TestChannel(channel_id=root_id, server=testlib.TestServer())
        for content in piper_messages:
            content = content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            msg = testlib.TestMessage(content=content, channel=channel, server=channel.server)
            self.assertTrue(self.piper._matches(msg), 'Match failed for %s, id=%s' %(content,msg.channel.id) )
            self.loop.run_until_complete(self.piper._action(msg))
            pipe_msg = find_by_channel_id(dest_id, self.bot.message_history)
            self.assertIsNotNone(pipe_msg, 'Piped message not found for %s, id=%s' %(content, msg.channel.id) )
            self.assertEqual(content, pipe_msg.content, 'Piped message not equal for %s' %content)
        # remove pipe
        self.piper.public_namespace.pipes.remove(test_pipe)

    def test_authorize(self):
        # set up pipe
        maintainer_id = '2'*18
        owner_id = '1'*18
        test_pipe = pipe_class.Pipe(name='test pipe', root_channel=root_id, channels=[dest_id], owner=owner_id)
        self.piper.public_namespace.pipes.append(test_pipe)
        # test authorize
        author = testlib.TestMember(user_id=owner_id)
        for content in authorize_messages:
            content = content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            content = content.replace('{maintainer-mention}', '<@!'+maintainer_id+'>')
            msg = testlib.TestMessage(content=content, author=author)
            self.assertTrue(self.pipe_authorize._matches(msg), 'Match failed for %s' %content )
            self.loop.run_until_complete(self.pipe_authorize._action(msg))
            # print(self.bot.last_message)
            # print(test_pipe.maintainers)
            self.assertIn(maintainer_id, test_pipe.maintainers, 'Correct maintainer not added for %s' %content )
        # remove pipe
        self.piper.public_namespace.pipes.remove(test_pipe)

    def test_modify(self):
        # set up pipe
        maintainer_id = '2'*18
        owner_id = '1'*18
        new_channel = '5'*18
        test_pipe = pipe_class.Pipe(name='test pipe', root_channel=root_id, channels=[dest_id], owner=owner_id, maintainers=[maintainer_id])
        self.piper.public_namespace.pipes.append(test_pipe)
        # test authorize
        author = testlib.TestMember(user_id=owner_id)
        channel = testlib.TestChannel(channel_id=new_channel)
        for content in modify_messages:
            content = content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            if '{channel-mention}' in content:
                content = content.replace('{channel-mention}', '<#'+new_channel+'>')
                channel.id = '0'*18
            msg = testlib.TestMessage(content=content, author=author, channel=channel)
            self.assertTrue(self.pipe_modify._matches(msg), 'Match failed for %s' %content )
            self.loop.run_until_complete(self.pipe_modify._action(msg))
            # print(self.bot.last_message)
            self.assertIn(new_channel, test_pipe.channels, 'Correct maintainer not added for %s' %content )
            test_pipe.channels.remove(new_channel)
            channel.id=new_channel
        # remove pipe
        self.piper.public_namespace.pipes.remove(test_pipe)

    def test_delete(self):
        maintainer_id = '2'*18
        owner_id = '1'*18
        for content in delete_messages:
            # create and add test pipe
            test_pipe = pipe_class.Pipe(name='test pipe', root_channel=root_id, channels=[dest_id], owner=owner_id)
            self.piper.public_namespace.pipes.append(test_pipe)
            # create discord test vars
            author = testlib.TestMember(user_id=owner_id)
            content = content.replace('{bot-mention}', '<@!'+self.bot.user.id+'>')
            msg = testlib.TestMessage(content=content, author=author)
            # test matches()
            self.assertTrue(self.pipe_delete._matches(msg))
            # test action()
            self.loop.run_until_complete(self.pipe_delete._action(msg))
            self.assertNotIn(test_pipe, self.piper.public_namespace.pipes, 'Test pipe not deleted for %s' %content)


def find_by_channel_id(id, iterable):
    for i in iterable:
        if i.channel.id == id:
            return i

def find_pipe_by_root(root, iterable):
    for i in iterable:
        if i.root_channel==root:
            return i

def find_pipe_by_channel(channel_id, iterable):
    for i in iterable:
        if channel_id in i.getAllChannels():
            return i
