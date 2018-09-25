from libs import command

class Command(command.Command):
    def matches(self, message):
        return "roles id" in message.content.lower() and message.server != None

    def action(self, message):
        result = "```\n name, id, colour\n"
        for role in message.server.roles:
            result += role.name+", "+role.id+", "+str(role.colour.value)+"\n"
        yield from self.send_message(message.channel, result+"```")
