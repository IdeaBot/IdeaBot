from libs import command

class Command(command.DirectOnlyCommand):
    '''Display roles and their IDs

**Usage**
To get roles info in the current server
```roles id```

**NOTE:** This is a debug command, so it may be removed or deprecated without notice in the future '''
    def matches(self, message):
        return "roles id" in message.content.lower() and message.server != None

    def action(self, message):
        result = "```\n name, id, colour\n"
        for role in message.server.roles:
            result += role.name+", "+role.id+", "+str(role.colour.value)+"\n"
        yield from self.send_message(message.channel, result+"```")
