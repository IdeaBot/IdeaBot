from libs import command
import random, re

class Command(command.DirectOnlyCommand):
    '''dice roll Command is a command that responds to messages asking for a random number'''

    def matches(self, message):
        return self._get_args(message) != None

    def action(self, message, send_func):
        args = self._get_args(message)
        if args.group(1) is None or args.group(2) is None:
            return
        if args.group(1) == 'a' or args.group(1) == 'an':
            num_to_roll = 1
        else:
            num_to_roll = int(args.group(1))
        if args.group(3) == 'coin':
            # coin has a special words in the response, so placed in separate block
            flips = []
            for i in range(num_to_roll):
                flips.append(random.choice(["heads", "tails"]))
            yield from send_func(message.channel,
                                 "Flipped %s coin%s and got %s" % (num_to_roll, ('' if num_to_roll == 1 else 's'), flips))
            return
        sides_to_roll = 6
        if args.group(2) != '':
            sides_to_roll = int(args.group(2))
        rolls = []
        for i in range(num_to_roll):
            rolls.append(random.randint(1,sides_to_roll))
        yield from send_func(message.channel,
                             "Rolled %s di%se and got %s" % (num_to_roll, ('' if num_to_roll == 1 else 'c'), rolls))

    def _get_args(self, message):
        '''
        Group 1 is the number of dice/coins to roll/flip.  If it's a roll, group 2
        is the sides on the dice.
        '''
        # roll regex tested at https://regexr.com/3r5n6
        # There is one case where this regex erros: roll # sided die will roll # 6-sided dice instead of 1 #-sided dice
        # flip regex tested at https://regexr.com/3r5nc
        return re.search(r'\broll\s+(an?|\d+(?!-))?\s*(\d*)\s?(?:-?sided)?\s*(die|dice)?', message.content, re.I) or re.search(r'\bflip\s+(a|\d+)()\s+(coin)?', message.content, re.I)