
import timezones, asyncio, dataloader, random, discord, sys
import time as timelib
config = dataloader.datafile("./data/config.config")
config.content = config.content["DEFAULT"]
perms = dataloader.datafile(config.content["permissionsloc"])
perms.content = perms.content["DEFAULT"]
snark = dataloader.datafile(config.content["snarkloc"])
evalDictOriginalNameThisIs = {}
@asyncio.coroutine
def interpretmsg(msg, client, qRedditURLAdder):
    '''(discord.msg object, DiscordClient object) -> None
    raises an exception if the msg cannot be interpreted, otherwise does the appropriate stuff'''
    startTime = timelib.time()
    msgcontentlower = msg.content.lower()
    try:
        if msg.author != client.user and msg.channel.permissions_for(msg.channel.server.me).send_messages: # everything past here will eventually become some super string parser
            if client.user.mention in msg.content:
                msgcontentlower = msgcontentlower.replace(client.user.mention, "")
                msgcontent = msg.content.replace(client.user.mention, "")
                if ("execute" in msgcontentlower or "evaluate" in msgcontentlower) and msg.author.id in perms.content["executionperm"]:
                    try:
                        if "```" in msgcontentlower:
                            result = eval(msgcontent[msgcontent.index("```")+3 : msgcontent.rindex("```")])
                        else:
                            result = eval(msgcontent[msgcontent.index("`")+1 : msgcontent.rindex("`")])
                        if result != None:
                            yield from client.send_message(msg.channel, result)
                        else:
                            yield from client.send_message(msg.channel, "Execution completed successfully")
                    except KeyboardInterrupt:
                        raise
                    except:
                        exception = sys.exc_info()
                        yield from client.send_message(msg.channel, "I'm sure it's a feature that your code crashes, right? " + "Your code raised this: " + str(exception[0]).replace("'>", "").replace("<class '", "") + ":" + str(exception[1]))
                elif "what" in msgcontentlower:
                    if (" id " in msgcontentlower or msg.content[-len(" id"):].lower() == " id") and " my " in msgcontentlower:
                        yield from client.send_message(msg.channel, msg.author.id)
                    if " in " in msgcontentlower:
                        time, timezoneTarget = timezones.getConversionParameters(msg.content)
                        yield from client.send_message(msg.channel, time.convertTo(timezoneTarget))
                elif "snark" in msgcontentlower:
                    if "list" in msgcontentlower:
                        yield from client.send_message(msg.channel, "``` " + str(snark.content) + " ```")
                    else:
                        yield from client.send_message(msg.channel, random.choice(snark.content))
                elif "ping" in msgcontentlower:
                    pass
                elif "add" in msgcontentlower and "`" in msgcontentlower: # add a url to the reddit watchlist
                    qRedditURLAdder.put({"action" : "add", "url" : msgcontent[msgcontent.index("`")+1 : msgcontent.rindex("`")]})
                    yield from client.send_message(msg.channel,"Ok, I'll try!")
                else: raise ValueError("That's a dumb message")
            else:
                '''if "hotdog" in msgcontentlower or "dick" in msgcontentlower or "hot-dog" in msgcontentlower:
                    yield from client.send_message(msg.channel, "Hotdog :)")
                elif "h" in msgcontentlower and "o" in msgcontentlower and "t" in msgcontentlower and "d" in msgcontentlower and "o" in msgcontentlower and "g" in msgcontentlower:
                    yield from client.send_message(msg.channel, "Not hotdog :(")'''
                if "blame josh" in msgcontentlower:
                    yield from client.send_message(msg.channel, "https://cdn.discordapp.com/attachments/382856950079291395/392398975686279168/unknown.png")
                if "forum post" in msgcontentlower:
                    yield from client.add_reaction(msg, config.content["forumpostemoji"])

            if msg.author.id in perms.content["shutdownperm"] and "shutdown protocol 0" in msgcontentlower: #if ngnius says shutdown
                yield from client.send_message(msg.channel, "Goodbye humans...")
                yield from client.logout()
    except ValueError:
        yield from client.send_message(msg.channel, config.content["invalidmessagemessage"])
    if "benchmark" in msgcontentlower and client.user.mention in msg.content:
        yield from client.send_message(msg.channel, "Executed in " + str(timelib.time()-startTime)+"s")

def test(a,b):
    '''(int,int) -> (int)'''
    c = a+b
    return c

def assign(a,b):
    '''(object, object) -> bool
    assigns b value in a global dict to a
    returns True if it creates a new key'''
    global evalDictOriginalNameThisIs
    if a in evalDictOriginalNameThisIs:
        output = False
    else:
        output = True
    evalDictOriginalNameThisIs[a] = b
    return output

def retrieve(a):
    '''(object) -> object
    retrieves a in evalDictOriginalNameThisIs
    Precondition: a must be in evalDictOriginalNameThisIs'''
    return evalDictOriginalNameThisIs[a]
