from commands import command

class RolesCommand(command.Command):
    def matches(self, message):
        return "roles id" in message.content.lower() and message.server != None

    def action(self, message, send_func):
        result = "```\n"
        for role in message.server.roles:
            result += "name: "+role.name+", id: "+role.id+", colour: "+str(role.colour.value)+"\n"
        yield from send_func(message.channel, result+"```")
