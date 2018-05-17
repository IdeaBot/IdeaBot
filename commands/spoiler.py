from commands import command
from libs import embed
import re

class Spoiler(command.DirectOnlyCommand):
    def matches(self, message):
        args = re.search(r'\bspoiler\s([\d]{1,2})', message.content, re.I)
        return args != None
    def action(self, message, send_func):
        args = re.search(r'\bspoiler\s([\d]{1,2})', message.content, re.I)
        msgEmbed = embed.create_embed(title="SPOILERS!", author={"name":"River Song", "url":None, "icon_url":None}, description=int(args.group(1))*".\n"+"^^^ WARNING: Spoiler Above ^^^")
        yield from send_func(message.channel, embed=msgEmbed)
