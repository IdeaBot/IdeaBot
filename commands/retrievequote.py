from libs import command
from libs import embed, dataloader
import re, os

SAVE_LOC = 'saveloc'

class Command(command.Config):
    '''Retrieves saved quotes

**Usage**
To display message with ID <message id>
```<message id>```
Where
**`<message id>`** is the ID of a saved message '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.saveloc = self.config[SAVE_LOC]

    def matches(self, message):
        result = re.search(r'(\d{18})', message.content)
        return result != None and str(result.group(1))+".txt" in os.listdir(self.saveloc)

    def action(self, message):
        quotedMessage = eval(dataloader.datafile(self.saveloc+"/"+re.search(r'(\d{18})', message.content).group(1)+".txt").content[0])
        em = embed.create_embed(author={"name":quotedMessage["author"], "url":None, "icon_url":None},
            footer={"text": "#"+quotedMessage["channel"]+" of "+quotedMessage["server"], "icon_url":None},
            description=quotedMessage["content"],
            colour=0xffffff)
        yield from self.send_message(message.channel, embed=em)
