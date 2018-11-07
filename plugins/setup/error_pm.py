from libs import plugin, embed
import discord, traceback, asyncio

class Plugin(plugin.AdminPlugin):
    '''Dummy plugin for modifying the error catching methods of the bot.
    The methods are modified in order to send PMs to the owner of the add-on'''
    def on_client_add(self):
        self.bot.on_command_error=self.on_command_error
        self.bot.on_reaction_error=self.on_reaction_error

    @asyncio.coroutine
    def on_command_error(self, cmd_name, error):
        if cmd_name not in self.public_namespace.commanders[self.public_namespace.COMMANDS]:
            commanders2 = self.generate_commanders(self.bot)
            self.merge_commanders(commanders2)
        user_id = self.public_namespace.commanders[self.public_namespace.COMMANDS][cmd_name][self.public_namespace.OWNER]
        user = discord.utils.find(lambda u: u.id == user_id, self.bot.get_all_members())
        if user:
            title = '**%s** (command) raised an exception during execution' %cmd_name
            desc = '```'+(''.join(traceback.format_exc()))+'```'
            footer = {'text':'This was sent to you because your are registered as the owner of this command', 'icon_url':None}
            em = embed.create_embed(footer=footer, title=title, description=desc, colour=0xff1111)
            try:
                yield from self.send_message(user, embed=em)
            except:
                traceback.print_exc()
                pass

    @asyncio.coroutine
    def on_reaction_error(self, cmd_name, error):
        if cmd_name not in self.public_namespace.commanders[self.public_namespace.REACTIONS]:
            commanders2 = self.generate_commanders(self.bot)
            self.merge_commanders(commanders2)
        user_id = self.public_namespace.commanders[self.public_namespace.REACTIONS][cmd_name][self.public_namespace.OWNER]
        user = discord.utils.find(lambda u: u.id == user_id, self.bot.get_all_members())
        if user:
            title = '**%s** (reaction) raised an exception during execution' %cmd_name
            desc = '```'+(''.join(traceback.format_exc()))+'```'
            footer = {'text':'This was sent to you because you are registered as the owner of this reaction', 'icon_url':None}
            em = embed.create_embed(footer=footer, title=title, description=desc, colour=0xff1111)
            try:
                yield from self.send_message(user, embed=em)
            except:
                traceback.print_exc()
                pass
