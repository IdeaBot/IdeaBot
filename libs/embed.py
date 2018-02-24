'''Lazy way to make discord embeds'''

import discord

def create_embed(footer=None, image=None, thumbnail=None, author=None, **kwargs):
    '''(dict, dict, dict, dict, dict) -> discord.Embed
    creates an embed without all the annoying stuff that you have to do with a regular embed'''
    embed = discord.Embed(**kwargs)
    if footer:
        footer = none2Empty(footer)
        embed.set_footer(**footer)
    if image:
        image = none2Empty(image)
        embed.set_image(**image)
    if thumbnail:
        thumbnail = none2Empty(thumbnail)
        embed.set_thumbnail(**thumbnail)
    if author:
        author = none2Empty(author)
        embed.set_author(author["name"], url=author["url"], icon_url=author["icon_url"])
    return embed

def none2Empty(dictionary):
    '''(dict) -> dict
    searches dictionary for any instances of None, and replaces them with discord.Embed.Empty'''
    dictionary = dict(dictionary)
    for i in dictionary:
        if dictionary[i] == None:
            dictionary[i] = discord.Embed.Empty
    return dictionary
