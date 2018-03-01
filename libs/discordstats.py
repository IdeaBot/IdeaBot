from libs import dataloader
import datetime

def dumpMessages(discordClient, filename = "./data/msgdump.csv", info = "timestamp.isoformat(timespec='seconds'),channel.name,server.name"):
    '''(discord.Client object, str, str) -> None
    dumps messages' info in discordClient.messages to filename'''
    global i, messages # horrible idea but it works
    messages = list(discordClient.messages)
    msgFile = dataloader.newdatafile(filename)
    infostrip = info.split(",")
    msgFile.content = [None]*len(messages)
    for i in range(len(messages)):
        msgFile.content[i] = [eval("messages[i]."+x) for x in infostrip]
        '''
        for j in info:
            try:
                msgFile.content[i].append(eval("messages[i]."+j))
            except:
                msgFile.content[i].append(" ")
        '''
    msgFile.save()

# shortcuts

def dumpMessagesTime(discordClient, filename = "./data/msgdump.csv"):
    dumpMessages(discordClient, filename=filename, info="timestamp.isoformat(timespec='seconds'),channel.name")

def dumpPlayerActivity(discordClient, filename = "./data/msgdump.csv", info="timestamp.isoformat(timespec='seconds'),author.name, author.id"):
    dumpMessages(discordClient, filename, info)

# not a shortcut, but still for the lazy

def runTimeReport(discordClient, interval=3600, filename="./data/msgtimedump.csv"):
    '''(discord.Client object, int) -> list of [datetime object, int]
    interval is interpreted as seconds
    analuses messages' times for data analysis purposes '''
    messages = discordClient.messages
    now = datetime.datetime.utcnow()
    results1 = [None]*((round((now - messages[-1].timestamp).total_seconds())//interval)+1)
    results2 = [None]*((round((now - messages[0].timestamp).total_seconds())//interval)+1)
    if len(results1) > len(results2):
        results = results1
    else:
        results = results2
    for i in range(len(results)):
        results[i] = [now-datetime.timedelta(seconds=(i*interval)%3600, hours=(i*interval)//3600), 0]
    for i in messages:
        delta = now - i.timestamp
        location = int(delta.total_seconds()) // interval
        results[location][1] += 1
    results = [[x[0].isoformat(timespec="seconds"), str(x[1])] for x in results]
    msgInfoFile = dataloader.newdatafile(filename)
    msgInfoFile.content = results
    msgInfoFile.save()
    return results

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
        msgFile.content[i] = [eval("messages[i]."+x) for x in infostrip]
        '''
        for j in info:
            try:
                msgFile.content[i].append(eval("messages[i]."+j))
            except:
                msgFile.content[i].append(" ")
        '''
    msgFile.save()
