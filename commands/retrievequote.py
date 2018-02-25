from commands import command
from libs import embed, dataloader
import re, os

class DisplayQuote(command.Command):
    def __init__(self, saveloc="./", **kwargs):
        super().__init__(**kwargs)
        self.saveloc = saveloc

    def matches(self, message):
        result = re.search(r'(\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d)\s*', message.content)
        return result != None and str(result.group(1))+".txt" in os.listdir(self.saveloc)

    def action(self, message, send_func):
        quotedMessage = eval(dataloader.datafile(self.saveloc+"/"+re.search(r'(\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d\d)\s*', message.content).group(1)+".txt").content[0])
        em = embed.create_embed(author={"name":quotedMessage["author"], "url":None, "icon_url":None},
            footer={"text": "#"+quotedMessage["channel"]+" of "+quotedMessage["server"], "icon_url":None},
            description=quotedMessage["content"],
            colour=0xffffff)
        yield from send_func(message.channel, embed=em)
