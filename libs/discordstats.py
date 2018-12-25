'''
Saves discord info to file. This is mainly used in debugging.

This is a collection of tools which take into account the discord.py memory structure
in order to save relevant and understandable data.

@author: NGnius
'''

from libs import dataloader
import datetime

# Dump messages to file

def dumpMessagesTime(discordClient, filename = "./data/msgdump.csv"):
    dumpMessages(discordClient, filename=filename, info="timestamp.isoformat(timespec='seconds'),channel.name")

def dumpPlayerActivity(discordClient, filename = "./data/msgdump.csv", info="timestamp.isoformat(timespec='seconds'),author.name, author.id"):
    dumpMessages(discordClient, filename, info)

def dumpMessagesTime(discordClient, filename = "./data/msgdump.csv"):
    messages = discordClient.messages
    msgFile = dataloader.newdatafile(filename)
    for i in messages:
        msgFile.content.append([i.timestamp.isoformat(timespec="seconds"), i.channel.name]) # yes I'm logging messages' contents right now, don't worry, nobody will see it
    msgFile.save()

def dumpMessages(discordClient, filename = "./data/msgdump.csv", info = "timestamp.isoformat(timespec='seconds'),id,channel.name,server.name"):
    '''(discord.Client object, str, str) -> None
    dumps messages' info in discordClient.messages to filename'''
    global i, messages # horrible idea but it works
    messages = list(discordClient.messages)
    msgFile = dataloader.newdatafile(filename)
    infostrip = info.split(",")
    msgFile.content = [None]*len(messages)
    for i in range(len(messages)):
        msgFile.content[i] = list()
        for j in infostrip:
            try:
                result = eval("messages[i]."+j)
            except:
                result = "None"
            msgFile.content[i].append(str(result))
        '''
        for j in info:
            try:
                msgFile.content[i].append(eval("messages[i]."+j))
            except:
                msgFile.content[i].append(" ")
        '''
    msgFile.save()

# convenience functions for live stats

def total_users(discordClient):
    total = 0
    for server in discordClient.servers:
        if not server.unavailable: # handle case where guilds go die in a whole due to Discord server issues
            total += len(server.members)
    return total
