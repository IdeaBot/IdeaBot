from libs import command, dataloader
import re, asyncio

FILENAME = 'commands/explorer/channels.csv'

class Command(command.Multi, command.DirectOnlyCommand):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # load channels that explorer Plugin will respond to
        self.public_namespace.exploring_file = dataloader.loadfile_safe(FILENAME, load_as='csv')
        self.public_namespace.exploring_channels = self.public_namespace.exploring_file.content

    def matches(self, message):
        # essentially checks for "explore channel" or "explore this channel"
        return re.search(r'explore\s*(?:this\s*)?channel', message.content, re.I)

    def action(self, message):
        send_func = self.send_message
        if message.channel.id in self.public_namespace.exploring_channels:
            del(self.public_namespace.exploring_channels[self.public_namespace.exploring_channels.index(message.channel.id)])
            yield from send_func(message.channel, 'Exploration **disabled** for this channel')
        else:
            self.public_namespace.exploring_channels.append(message.channel.id)
            yield from send_func(message.channel, 'Exploration **enabled** for this channel')

        # save channels that explorer Plugin will respond to
        self.public_namespace.exploring_file.content = self.public_namespace.exploring_channels
        self.public_namespace.exploring_file.save()

    def shutdown(self):
        # save channels that explorer Plugin will respond to
        self.public_namespace.exploring_file.content = self.public_namespace.exploring_channels
        self.public_namespace.exploring_file.save()
