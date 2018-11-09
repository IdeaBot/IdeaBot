from libs import command
import re

class Command(command.AdminCommand, command.DirectOnlyCommand):
    '''A command for setting which user can use which commands in your server

    **Usage:**
    ```@Idea (reaction OR command) perms -> <reaction/command name> <user mention>```

    The Permission Setter command is probably restricted to certain users
    **NOTE:** Set the permissions of this command to ensure no unauthorized user can change permissions for other commands '''
    def _matches(self, message): #ik it's bad form
        return ( message.server!=None and ( message.server.owner == message.author  and self.matches(message) ) ) or super()._matches(message)

    def matches(self, message):
        args = re.search(r'(reaction|command|\s?)\s?perms\s?->\s?(\S+)\s(\S+)', message.content, re.I)
        return args!=None

    def action(self, message, bot):
        send_func = self.send_message
        args = re.search(r'(reaction|command|\s?)\s?perms\s?->\s?(\S+)\s(\S+)', message.content, re.I)
        if args.group(2).lower() == 'all':
            user_id = self.get_perms(args.group(3), bot)
            if args.group(1)=="reaction":
                for reaction_name in bot.reactions:
                    if isinstance(bot.reactions[reaction_name].perms, list):
                        bot.reactions[reaction_name].perms.append(user_id)
                yield from send_func(message.channel, "Permissions set for all reactions")
            elif args.group(1)=="command":
                for command_name in bot.commands:
                    if isinstance(bot.reactions[command_name].perms, list):
                        bot.reactions[command_name].perms.append(user_id)
                yield from send_func(message.channel, "Permissions set for all commands")
            else:
                yield from send_func(message.channel, "You need to specify reaction or command to use this")
        elif args.group(2) in bot.commands and args.group(2) in bot.reactions and len(args.group(1))<=1:
            yield from send_func(message.channel, "A reaction and command matching %s were found. Please re-run this command and specify which one right before the rest of the command." % args.group(2))
        elif (args.group(1)=="command" or len(args.group(1))<=1) and args.group(2) in bot.commands:
            if bot.commands[args.group(2)].perms == None:
                yield from send_func(message.channel, "Perms cannot be set for %s " % args.group(2))
                return
            elif args.group(3).lower()=="all":
                if message.server.id in bot.commands[args.group(2)].perms:
                    del(bot.commands[args.group(2)].perms[message.server.id])
            elif args.group(3).lower()=="none":
                bot.commands[args.group(2)].perms[message.server.id] = list()
            elif message.server.id not in bot.commands[args.group(2)].perms:
                bot.commands[args.group(2)].perms[message.server.id] = self.get_perms(args.group(3), bot)
            else:
                bot.commands[args.group(2)].perms[message.server.id] += self.get_perms(args.group(3), bot)
            yield from send_func(message.channel, "Perms set for %s command" % args.group(2))
            bot.commands[args.group(2)]._shutdown()
        elif (args.group(1)=="reaction" or len(args.group(1))<=1) and args.group(2) in bot.reactions:
            if bot.reactions[args.group(2)].perms == None:
                yield from send_func(message.channel, "Perms cannot be set for %s " % args.group(2))
                return
            elif args.group(3).lower()=="all":
                if message.server.id in bot.reactions[args.group(2)].perms:
                    del(bot.reactions[args.group(2)].perms[message.server.id])
            elif args.group(3).lower()=="none":
                bot.reactions[args.group(2)].perms[message.server.id] = list()
            elif message.server.id not in bot.reactions[args.group(2)].perms:
                bot.reactions[args.group(2)].perms[message.server.id] = self.get_perms(args.group(3), bot)
            else:
                bot.reactions[args.group(2)].perms[message.server.id] += self.get_perms(args.group(3), bot)
            yield from send_func(message.channel, "Perms set for %s reaction" % args.group(2))

    def get_perms(self, mention, bot):
        user_list = mention.split(">")
        num=0
        while num<len(user_list):
            if user_list[num][:2]=="<@":
                user_list[num]=user_list[num][2:]
                num+=1
            else:
                del(user_list[num])
        return user_list
