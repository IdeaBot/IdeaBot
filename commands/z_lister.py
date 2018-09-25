from libs import command
import re

class Command(command.DirectOnlyCommand, command.AdminCommand):
    def matches(self, message):
        return re.search(r'list\s*([^\s\(\)]+)', message.content, re.I) != None

    def action(self, message, bot):
        args = re.search(r'list\s*([^\s\(\)]+)', message.content, re.I)
        try:
            reply = process_list(eval("bot."+args.group(1)))
        except AttributeError:
            yield from self.send_message(message.channel, "Couldn't find the variable")
        except IndexError:
            yield from self.send_message(message.channel, "Invalid list chosen")
        except TypeError:
            yield from self.send_message(message.channel, "Chosen item is not listable")
        except SyntaxError:
            yield from self.send_message(message.channel, "I'm sorry, what?")
        else:
            yield from self.send_message(message.channel, reply)

def process_list(iterable):
    result = "\n"
    for i in iterable:
        result+=str(i)+'\n'
    return result
