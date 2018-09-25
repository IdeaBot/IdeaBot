from libs import command
from libs import discordstats
import re

FILEPATH="msgdumptemp.csv"

class Command(command.DirectOnlyCommand):
    def matches(self, message):
        return re.search(r'stats|statistics', message.content, re.I)!=None

    def action(self, message):
        discordstats.dumpMessages(client, filename=FILEPATH, info="timestamp.isoformat(timespec='seconds'),author.name,id,channel.name,server.name")
        yield from self.send_file(message.channel,FILEPATH)
