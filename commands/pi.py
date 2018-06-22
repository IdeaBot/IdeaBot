from libs import command
from libs import dataloader

class Command(command.DirectOnlyCommand, command.Config):

    def matches(self, message):
        return " pi " in message.content.lower() or " pi" == message.content.lower()[-3:] or "pi " == message.content.lower()[:3]

    def action(self, message, send_func):
        yield from send_func(message.channel, self.config.content[1][int(self.config.content[0])])
        self.config.content[0]= str(int(self.config.content[0])+1)
        self.config.save()
