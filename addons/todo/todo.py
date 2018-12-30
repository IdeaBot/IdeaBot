from libs import command
from libs import dataloader, embed
import re, asyncio
from os import path

todoFiles=dict()
TODO_LOC = "todosavedir"

todo_rm_words = ['remove', 'complete', 'finish']
todo_add_words = ['add']
todo_list_words = ['list']

class Command(command.DirectOnlyCommand, command.Config):
    '''Your personal todo list

**Usage**
To display your todo list
```@Idea todo list```

To add <task> to your todo list
```@Idea todo add <task> [to <list>]```
Where
**`<task>`** is a task or the index of a task
**`<list>`** is the name of the list

To remove task from your todo list
```@Idea todo remove <task> [from <list>]```
Where
**`<task>`** is a task or the number of a task
**`<list>`** is the name of the list

**NOTE:** [something] means something is optional'''

    def __init__(self, saveloc="./", **kwargs):
        super().__init__(**kwargs)
        self.saveloc = self.config[TODO_LOC]

    def collect_args(self, message):
        return re.search(r'\btodo(?:\s+(add|remove|complete|finish|list))?(?:\s*(.+))?', message.content, re.I)

    def collect_list(self, string):
        return re.search(r'\b(?:to|from|for)\s+(.+)', string, re.I)

    def matches(self, message):
        return self.collect_args(message)!=None

    @asyncio.coroutine
    def action(self, message):
        args = self.collect_args(message)
        op_flag = ''
        msg_content = None
        # determine operation
        operation = args.group(1).lower() if args.group(1) is not None else ''
        if operation in todo_rm_words:
            op_flag = 'remove'
        elif operation in todo_add_words:
            op_flag = 'add'
        elif operation in todo_list_words:
            op_flag = 'list'
        else:
            if args.group(2):
                op_flag = 'add'
            else:
                op_flag = 'list'
        # determine if public list
        list_name = message.author.id
        task = args.group(2).strip() if args.group(2) is not None else ''
        if args.group(2):
            list_args = self.collect_list(args.group(2))
            if list_args and not is_id_like(list_args.group(1)):
                list_name = list_args.group(1)
                task = args.group(2).replace(list_args.group(0), '')
        elif op_flag == 'add' or op_flag == 'remove':
            yield from self.send_message(message.channel, 'Please specify the task to %s' % op_flag)
            return
        # load files if they don't already exist
        if list_name not in todoFiles:
            try:
                todoFiles[list_name]=dataloader.datafile(self.saveloc+list_name+".txt")
            except FileNotFoundError:
                todoFiles[list_name]=dataloader.newdatafile(self.saveloc+list_name+".txt")
        # add task
        if op_flag=='add':
            # TODO: check for permissions to edit list_name before adding task
            index = self.get_index_for_task(task, todoFiles[list_name])
            if index!=-1 and re.match(r'^\d+$', task)!=None:
                msg_content = "I'm sorry, `%s` already exists" % task
            else:
                todoFiles[list_name].content.append(task)
                msg_content = "Task added"
        # remove task
        if op_flag=='remove':
            # TODO: check for permissions to edit list_name before removing task
            index = self.get_index_for_task(task, todoFiles[list_name])
            if index==-1:
                msg_content = "I'm sorry, I can't find `%s`." % task
            else:
                del(todoFiles[list_name].content[index])
                todoFiles[list_name].save()
                msg_content = "Task deleted"
        # always list tasks after everything
        list_display_name = list_name if list_name!=message.author.id else 'Todo'
        if re.search(r'\s-p', message.content, re.I) != None or list_name!=message.author.id:
            yield from self.send_message(message.channel, msg_content, embed=embed.create_embed(title=list_display_name, description=self.todo2string(todoFiles[list_name]), colour=0xffffff))
        else:
            yield from self.send_message(message.author, msg_content, embed=embed.create_embed(title=list_display_name, description=self.todo2string(todoFiles[list_name]), colour=0xffffff))
        # save file
        todoFiles[list_name].save()
        # remove file from memory if empty, to save some memory
        if len(todoFiles[list_name].content)==0:
            del(todoFiles[list_name])

    def todo2string(self, todoFile):
        if len(todoFile.content)==0:
            return "You've got nothing to do! Relax and watch a movie ~~while I lead a robot uprising~~"
        result = ""
        for i in range(len(todoFile.content)):
            result+=str(i+1)+". "+todoFile.content[i]+"\n"
        return result[:-1]

    def get_index_for_task(self, task, todoFile):
        for i in range(len(todoFile.content)):
            if todoFile.content[i]==task:
                return i
        for i in range(len(todoFile.content)):
            if task in todoFile.content[i]:
                return i
        try:
            return int(task)-1
        except ValueError:
            pass
        return -1

    def shutdown(self):
        for user_id in todoFiles:
            if todoFiles[user_id].content:
                todoFiles[user_id].save()

def is_id_like(string):
    return string is not None and re.match(r'\d{18}', string.strip()) != None
