from libs import command
import re

class Command(command.DirectOnlyCommand, command.AdminCommand):
    def matches(self, message):
        return re.search(r'list\s*([^\s\(\)]+)', message.content, re.I) != None

    def action(self, message, send_func, bot):
        args = re.search(r'list\s*([^\s\(\)]+)', message.content, re.I)
        try:
            reply = process_list(eval("bot."+args.group(1)))
        except AttributeError:
            yield from send_func(message.channel, "Couldn't find the variable")
        except IndexError:
            yield from send_func(message.channel, "Invalid list chosen")
        except TypeError:
            yield from send_func(message.channel, "Chosen item is not listable")
        except SyntaxError:
            yield from send_func(message.channel, "I'm sorry, what?")
        else:
            yield from send_func(message.channel, reply)

def process_list(iterable):
    result = "\n"
    for i in iterable:
        result+=str(i)+'\n'
    return result
