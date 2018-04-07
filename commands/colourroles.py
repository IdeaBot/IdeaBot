from commands import command
import discord, asyncio, time

dc = discord.Colour
RAINBOW = {dc.teal():"teal", dc.dark_teal():"dark_teal", dc.green():"green", dc.dark_green():"dark_green", dc.blue():"blue", dc.dark_blue():"dark_blue", dc.purple():"purple", dc.dark_purple():"dark_purple", dc(0xFF00FF):"magenta", dc(0xAF00AF):"dark_magenta", dc.gold():"gold", dc.dark_gold():"dark_gold", dc.orange():"orange", dc.dark_orange():"dark_orange", dc.red():"red", dc.dark_red():"dark_red", dc.lighter_grey():"lighter_grey", dc.dark_grey():"dark_grey", dc.darker_grey():"darker_grey", dc(0x000000):"black", dc(0xffffff):"white", dc(0x990d29):"TNT", dc(0xFFC0CB):"pink", dc(0xF5F5DC):"beige", dc(0x964B00):"brown"}
EMOJIS = ['🌎', '🌍', '☘️', '🎬', '🔵', '🐬', '🦄', '🐋', '🔮', '⚜', '💛', '⚠', '🔶', '🔅', '🔴', '🐞', '🌖', '🌗', '🌘', '🌑','🌕','💣', '🐖', '🏷', '🍪']
SPEED = 0
RAINBOW_MESSAGE = "React with these emojis to get the corresponding colour: \n"
n=0
for i in RAINBOW:
    RAINBOW_MESSAGE+=RAINBOW[i]+" : "+EMOJIS[n]+"\n"
    n+=1

class CreateColourRoleMessage(command.AdminCommand, command.DirectOnlyCommand):
    def __init__(self, role_messages, **kwargs):
        super().__init__(**kwargs)
        self.role_messages=role_messages
    def matches(self, message):
        return "create colour role message" in message.content.lower()

    @asyncio.coroutine
    def action(self, message, send_func, bot, speed=SPEED):
        yield from deleteColourRoles(message.server, bot)
        n=1 #len(EMOJIS)
        colourRoleDict = dict()
        for colour in RAINBOW:
            newRole = yield from bot.create_role(message.server, colour=colour, name=RAINBOW[colour])
            yield from bot.move_role(message.server, newRole, n)
            colourRoleDict[EMOJIS[n-1]] = discord.Object(newRole.id)
            n+=1
            time.sleep(speed)
        roleMessage = yield from send_func(message.channel, RAINBOW_MESSAGE)
        self.role_messages[roleMessage.id]=colourRoleDict

class DeleteColourRoles(command.AdminCommand, command.DirectOnlyCommand):
    def matches(self,message):
        return "remove colour roles" in message.content.lower()

    @asyncio.coroutine
    def action(self, message, send_func, bot):
        count = yield from deleteColourRoles(message.server, bot)
        yield from send_func(message.channel, "Deleted "+str(count)+" roles. Rerun this if I missed something - I'm sort of a pacifist.")

def deleteColourRoles(server, bot, speed=SPEED):
    count = 0
    for role in server.roles:
        for colour in RAINBOW:
            if RAINBOW[colour].lower().strip() == role.name.lower().strip():
                yield from bot.delete_role(server, role)
                count += 1
                break
        time.sleep(speed)
    return count

def deleteAllRoles(server, bot, speed=SPEED):
    for role in server.roles:
        yield from bot.delete_role(server, role)
        time.sleep(speed)
