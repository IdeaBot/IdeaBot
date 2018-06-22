from libs import command
import re

class Command(command.Multi, command.AdminCommand, command.DirectOnlyCommand):
    def matches(self, message):
        args = re.search(r'(reaction|command|\s?)\s?perms\s?->\s?(\S+)\s(\S+)', message.content, re.I)
        return args!=None

    def action(self, message, send_func, bot):
        print("Yo")
        args = re.search(r'(reaction|command|\s?)perms\s?->\s?(\S+)\s(\S+)', message.content, re.I)
        if args.group(2) in bot.commands and args.group(2) in bot.reactions and len(args.group(1))<=1:
            yield from send_func(message.channel, "A reaction and command matching %s were found. Please re-run this command and specify which one right before the rest of the command." % args.group(2))
        elif (args.group(1)=="command" or len(args.group(1))<=1) and args.group(2) in bot.commands:
            if bot.commands[args.group(2)].perms == None:
                bot.commands[args.group(2)].perms = self.get_perms(args.group(3), bot)
            else:
                bot.commands[args.group(2)].perms += self.get_perms(args.group(3), bot)
            yield from send_func(message.channel, "Perms set for %s command" % args.group(2))
        elif (args.group(1)=="reaction" or len(args.group(1))<=1) and args.group(2) in bot.reactions:
            if bot.reactions[args.group(2)].perms == None:
                bot.reactions[args.group(2)].perms = self.get_perms(args.group(3), bot)
            else:
                bot.reactions[args.group(2)].perms += self.get_perms(args.group(3), bot)
            yield from send_func(message.channel, "Perms set for %s reaction" % args.group(2))

    def get_perms(self, mention, bot):
        print(mention)
        user_list = mention.split(">")
        num=0
        while num<len(user_list):
            if user_list[num][:2]=="<@":
                user_list[num]=user_list[num][2:]
                num+=1
            else:
                del(user_list[num])
        print(user_list)
        return user_list
