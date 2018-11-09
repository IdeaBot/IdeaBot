from libs import command
from libs import dataloader, embed
import re, asyncio

todoFiles=dict()
TODO_LOC = "todosavedir"

class Command(command.DirectOnlyCommand, command.Config):
    '''Your personal todo list

    **Usage:**
    To display your todo list
    ```@Idea todo```
    
    To add <task> to your todo list
    ```@Idea todo <task>```

    To remove task in position <number> of your todo list
    ```@Idea remove <number>``` '''
    def __init__(self, saveloc="./", **kwargs):
        super().__init__(**kwargs)
        self.saveloc = self.config[TODO_LOC]

    def matches(self, message):
        return re.search(r'\bto\s?do:?\s*', message.content, re.I)!=None

    @asyncio.coroutine
    def action(self, message):
        if message.author.id not in todoFiles:
            try:
                todoFiles[message.author.id]=dataloader.datafile(self.saveloc+message.author.id+".txt")
            except FileNotFoundError:
                todoFiles[message.author.id]=dataloader.newdatafile(self.saveloc+message.author.id+".txt")
        args = re.search(r'\bto\s?do:?\s*["]?([^"-]*)["]?', message.content, re.I)
        if args==None or "list" in args.group(1).lower() or args.group(1)=="" or args.group(1)[0]=="-":
            if re.search(r'\s-p', message.content, re.I) != None:
                yield from self.send_message(message.channel, embed=embed.create_embed(author={"name":message.author.display_name+"'s To Do List", "url":None, "icon_url":None}, description=self.todo2string(todoFiles[message.author.id]), colour=0xffffff))
            else:
                yield from self.send_message(message.author, embed=embed.create_embed(author={"name":message.author.display_name+"'s To Do List", "url":None, "icon_url":None}, description=self.todo2string(todoFiles[message.author.id]), colour=0xffffff))
            return
        args2 = re.search(r'(complete|finish|remove)\s*(\d+)',args.group(1), re.I)
        if args2!=None and args2.group(2)!="" and int(args2.group(2).lower()) in range(1, len(todoFiles[message.author.id].content)+1):
            del(todoFiles[message.author.id].content[int(args2.group(2))-1])
            todoFiles[message.author.id].save()
            if len(todoFiles[message.author.id].content)==0:
                del(todoFiles[message.author.id])
            return
        todoFiles[message.author.id].content.append(args.group(1))
        #todoFiles[message.author.id].save()

    def todo2string(self, todoFile):
        if len(todoFile.content)==0:
            return "You've got nothing to do! Relax and watch a movie ~~while I lead a robot uprising~~"
        result = ""
        for i in range(len(todoFile.content)):
            result+=str(i+1)+". "+todoFile.content[i]+"\n"
        return result[:-1]

    def shutdown(self):
        for user_id in todoFiles:
            if todoFiles[user_id].content:
                todoFiles[user_id].save()
