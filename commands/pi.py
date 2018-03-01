from commands import command
from libs import dataloader

class PiCommand(command.DirectOnlyCommand):
    def __init__(self, filename, **kwargs):
        super().__init__(**kwargs)
        self.pifile = dataloader.datafile(filename)

    def matches(self, message):
        return " pi " in message.content.lower() or " pi" == message.content.lower()[-3:] or "pi " == message.content.lower()[:3]

    def action(self, message, send_func):
        yield from send_func(message.channel, self.pifile.content[1][int(self.pifile.content[0])])
        self.pifile.content[0]= str(int(self.pifile.content[0])+1)
        self.pifile.save()
