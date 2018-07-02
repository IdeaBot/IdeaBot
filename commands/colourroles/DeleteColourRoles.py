from libs import command
import discord, asyncio, time

dc = discord.Colour
RAINBOW = {dc.teal():"teal", dc.green():"green", dc.dark_green():"dark_green",
dc.blue():"blue", dc.dark_blue():"dark_blue", dc.purple():"purple",
dc(0xFF00FF):"magenta", dc.gold():"gold", dc.orange():"orange",
dc.red():"red", dc.dark_red():"dark_red", dc.lighter_grey():"lighter_grey",
dc.darker_grey():"darker_grey", dc(0x010101):"black", dc(0xffffff):"white", dc(0xFFC0CB):"pink", dc(0x964B00):"brown"}
EMOJIS = ['🌎', '☘', '🎬', '🔵', '🐬', '🦄', '🔮', '💛', '🔶', '🔴', '🐞', '🌖', '🌘', '🌑','🌕', '🐖', '🍪']
SPEED = 0.001
RAINBOW_MESSAGE = "React with these emojis to get the corresponding colour: \n"
n=0
for i in RAINBOW:
    RAINBOW_MESSAGE+=RAINBOW[i]+" : "+EMOJIS[n]+"\n"
    n+=1


class Command(command.AdminCommand, command.DirectOnlyCommand):
    def matches(self,message):
        return "remove colour roles" in message.content.lower()

    @asyncio.coroutine
    def action(self, message, send_func, bot):
        count = yield from deleteColourRoles(message.server, bot)
        yield from send_func(message.channel, "Deleted "+str(count)+" rainbow roles")

@asyncio.coroutine
def deleteColourRoles(server, bot, speed=SPEED):
    count = 0
    to_delete = list()
    # create list of roles to delete
    # NOTE: Deleting roles at the same time as iterating causes undesired results (lots of roles get skipped/missed)
    for role in server.roles:
        for colour in RAINBOW:
            if RAINBOW[colour].lower().strip() == role.name.lower().strip():
                to_delete.append([server, role])
                break
    # delete those roles
    for arg in to_delete:
        yield from bot.delete_role(*arg)
        count+=1
    return count
