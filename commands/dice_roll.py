from libs import command
import random, re

class Command(command.DirectOnlyCommand):
    '''dice roll Command is a command that responds to messages asking for a random number'''

    def matches(self, message):
        return re.search(r'\broll\s(a\s*)?(\d*)\s*(?:-?sided)?\s*(die|dice)?', message.content, re.I) != None or re.search(r'\bflip\s(a\s*)?(\d*)\s*(coin)?', message.content, re.I) != None

    def action(self, message, send_func):
        args = re.search(r'\broll\s(a\s*)?(\d*)\s*(?:-?sided)?\s*(die|dice)?', message.content, re.I) or re.search(r'\bflip\s(a\s*)?(\d*)\s*(coin)?', message.content, re.I)
        if not args.group(2):
            if args.group(3)=='coin':
                yield from send_func(message.channel, "Flipped a coin and got %s" % random.choice(["heads", "tails"]))
            elif args.group(3)=='die' or args.group(3)=='dice':
                yield from send_func(message.channel, "Rolled a "+args.group(3)+" and got "+str(random.randint(1,6)))
            else:
                yield from send_func(message.channel, "Rolled an undetermined sided die and got an undetermined number")
        else:
            if args.group(3):
                yield from send_func(message.channel, "Rolled a "+args.group(3)+" and got "+str(random.randint(1,int(args.group(2)))))
            else:
                yield from send_func(message.channel, "Rolled and got "+str(random.randint(1,int(args.group(2)))))
