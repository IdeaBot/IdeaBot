from libs import command, embed
import re, discord

class Command(command.DirectOnlyCommand):
    '''Add server status message to be populated by `cardlife_server_status`

**Usage**
```@Idea add cardlife server status ```

Please do not overuse this command - respect the CardLife servers'''
    def collect_args(self, message):
        return re.search(r'\b(?:get|add|create)\s*(?:cardlife|cl)\s*(?:server)?\s*status', message.content, re.I)
    def matches(self, message):
        return self.collect_args(message)!=None

    def action(self, message):
        description='**Future location of a server status message**'
        footer=dict()
        footer['text'] = '(Unofficial) CardLife API'
        footer['icon_url'] = None
        em = embed.create_embed(description=description, footer=footer)
        try:
            msg = yield from self.send_message(message.channel, embed=em)
        except discord.errors.DiscordException:
            yield from self.send_message(message.channel, 'Failed to create embed here, please make sure I have permission to embed links & stuff.')
        self.public_namespace.messages[msg.id]=msg.channel.id
        self.public_namespace.messages_file.content=self.public_namespace.messages
        self.public_namespace.messages_file.save()
