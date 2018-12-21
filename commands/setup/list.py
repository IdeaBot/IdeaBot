from libs import command, embed
import re

class Command(command.DirectOnlyCommand, command.AdminCommand):
    '''Provides a nice list to summarize Idea's functionality

The list of commands/reactions/plugins is provided in the following form:

**package name**
--command/reaction/plugin name

**Usage**
```@Idea list (commands/reactions/plugins)```
*(respectively)*

**NOTE:** Most package names do not work with `help`
**__WARNING:__** This command has been deprecated. Please use `help (commands/reactions/plugins)` instead '''
    def matches(self, message):
        return self.collect_args(message) != None

    def action(self, message, bot):
        args = self.collect_args(message)
        response_channel = message.author if '-p' not in message.content else message.channel
        addons = eval("bot."+args.group(1))
        #print(addons)
        addon_type = get_type(args.group(1))
        addons_dict=dict()
        for i in addons:
            pkg = bot.get_package(i, addon_type)
            if pkg not in addons_dict:
                addons_dict[pkg]=list()
            addons_dict[pkg].append(i)

        em = make_embed(addons_dict)
        em.title = 'My '+args.group(1).lower()
        yield from self.send_message(response_channel, embed=em)

    def collect_args(self, message):
        return re.search(r'\blist\s+(?:your\s)?((?:command|reaction|plugin)s)', message.content, re.I)

def process_list(iter, prefix='', suffix=''):
    result = ''
    for i in iter:
        if str(i)[0] not in FIRST_LETTER_BLACKLIST and passes_filter(str(i)):
            result+=prefix+str(i)+suffix+'\n'
    return result

def make_embed(addons_dict, colour=0xff00ff):
    footer={'text':'@Idea help <item> for more info', 'icon_url':None}
    desc = ''
    for key in addons_dict:
        if key is not None: # display package-less add-ons at the bottom
            desc+='**'+key+'**'+'\n'
            desc+=process_list(addons_dict[key], prefix='--')
    desc+='**'+'[NO PACKAGE]'+'**'+'\n'
    desc+=process_list(addons_dict[None], prefix='--')
    em = embed.create_embed(description=desc, footer=footer, colour=colour)
    return em


def passes_filter(string):
    return re.match(r'(.)\1*\_', string) is None

def get_type(string):
    return string.lower()
