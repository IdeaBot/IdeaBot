from libs import command, dataloader
import requests, traceback, re
from os.path import join, exists
from os import makedirs

COMMANDS_DIR = './commands'
REACTIONS_DIR = './reactions'

class Command(command.DirectOnlyCommand, command.AdminCommand, command.Multi):
    '''download_command downloads an attached python file (well, hopefully it's a Python file)

    This command will respond with any error caused by trying to download or save the file'''

    def matches(self, message):
        return re.search(r'download\s*(command|reaction)\s*(?:to\s*)?(\S+)?', message.content, re.I)!=None and len(message.attachments)>0

    def action(self, message, send_func, bot):
        args=re.search(r'download\s*(command|reaction)\s*(?:to\s*)?(\S+)?', message.content, re.I)
        try:
            for attachment in message.attachments:
                # NOTE: new_command_file should probably be a binary file (like open(filename, "wb") ), not a regular file
                # TODO(NGnius): make new_command_file a binary file (wb)
                if args.group(2):
                    # make sure folder exists
                    temp = args.group(2).replace("\\", "/").strip("/")
                    if "/" in temp:
                        folder = temp[:temp.rfind("/")]
                    else:
                        folder=temp
                    if args.group(1)=="command":
                        directory = join(COMMANDS_DIR, folder)
                    else:
                        directory = join(REACTIONS_DIR, folder)
                    if not exists(directory):
                        makedirs(directory)

                    # save file to correct location
                    if args.group(2).strip("\\/")[-3:]==".py":
                        if args.group(1)=="command":
                            new_command_file = dataloader.newdatafile(join(COMMANDS_DIR, args.group(2)))
                        else:
                            new_command_file = dataloader.newdatafile(join(REACTIONS_DIR, args.group(2)))
                    else:
                        if args.group(1)=="command":
                            new_command_file = dataloader.newdatafile(join(COMMANDS_DIR, args.group(2), attachment["filename"]))
                        else:
                            new_command_file = dataloader.newdatafile(join(REACTIONS_DIR, args.group(2), attachment["filename"]))
                else:
                    if args.group(1)=="command":
                        new_command_file = dataloader.newdatafile(join(COMMANDS_DIR, attachment["filename"]))
                    else:
                        new_command_file = dataloader.newdatafile(join(REACTIONS_DIR, attachment["filename"]))
                new_command_file.content = [requests.get(attachment["url"]).content.decode()]
                new_command_file.save()
                self.public_namespace.most_recent_download = new_command_file.filename
                yield from send_func(message.channel, "Successfully downloaded "+attachment["filename"])
        except:
            yield from send_func(message.channel, "```"+traceback.format_exc()+"```")
