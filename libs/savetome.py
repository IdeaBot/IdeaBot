from libs import dataloader, voting
import discord

MODE = "mode"
VOTES = "votes"
NAME = "name"
VALID_MODES=["fptp", "stv", ""]

def save_vote_dict(filename, vote_dict):
    '''(str, dict) -> None
    Saves vote_dict to filename in a format interpretable by load_vote_dict(filename)'''
    vote_dict_file = dataloader.newdatafile(filename)
    new_vote_dict=dict()
    for poll_msg_id in vote_dict:
        new_vote_dict[poll_msg_id]=vote_dict[poll_msg_id]
        new_vote_dict[poll_msg_id][VOTES]=vote_dict[poll_msg_id][VOTES].__dict__ #dict representation of variables contained in Poll object
    vote_dict_file.content = new_vote_dict
    vote_dict_file.save(save_as="json")

def load_vote_dict(filename):
    '''(str) -> dict
    Loads vote_dict from filename'''
    vote_dict=dict()
    try:
        vote_dict = dataloader.datafile(filename, load_as="json").content
    except:
        print("The %a file is either missing or corrupted; unable to load" %filename)
    finally:
        for poll_msg_id in vote_dict:
            if vote_dict[poll_msg_id][MODE] == 'stv':
                vote_dict[poll_msg_id][VOTES]=voting.STV(**vote_dict[poll_msg_id][VOTES])
            elif vote_dict[poll_msg_id][MODE] in VALID_MODES:
                vote_dict[poll_msg_id][VOTES]=voting.FPTP(**vote_dict[poll_msg_id][VOTES])
            else:
                try:
                    vote_dict[poll_msg_id][VOTES]=Poll(**vote_dict[poll_msg_id][VOTES])
                except:
                    del(vote_dict[poll_msg_id])
        return vote_dict

def save_ballot(filename, ballot):
    '''(str, dict) -> None
    Saves ballot to filename in a format interpretable by load_ballot(filename)
    In this case it's simply converted to JSON format'''
    ballot_file = dataloader.newdatafile(filename)
    ballot_file.content = ballot
    ballot_file.save(save_as="json")

def load_ballot(filename):
    ballot=dict()
    try:
        ballot = dataloader.datafile(filename, load_as="json").content
    except:
        print("The %a file is either missing or corrupted; unable to load" %filename)
    finally:
        return ballot

def save_role_messages(filename, role_messages):
    '''(str) -> None
    saves role_messages dictionary to a json that is readable from load_role_messages(filename)'''
    role_messages_file = dataloader.newdatafile(filename)
    new_role_messages = dict()
    for msg_id in role_messages:
        new_role_messages[msg_id]=dict()
        for emoji in role_messages[msg_id]:
            if str(emoji)==emoji: # if unicode emoji
                new_role_messages[msg_id][emoji]=role_messages[msg_id][emoji].id # turns into dict of {<emoji char>:discord.Role.id}
            else:
                new_role_messages[msg_id][emoji.id]=role_messages[msg_id][emoji].id # turns into dict of {discord.Emoji.id:discord.Role.id}
    role_messages_file.content = new_role_messages
    role_messages_file.save(save_as='json')

def load_role_messages(filename, all_emojis_func):
    '''(str) -> dict
    loads role_messages dictionnary from file filename and returns it'''
    role_messages = dict()
    try:
        role_messages_file = dataloader.datafile(filename, load_as='json')
    except:
        print("The %a file is either missing or corrupted; unable to load" %filename)
        return dict()

    for msg_id in role_messages_file.content:
        role_messages[msg_id]=dict()
        for emoji_id in role_messages_file.content[msg_id]:
            role_messages[msg_id][matchemoji(all_emojis_func, emoji_id)]=discord.Object(role_messages_file.content[msg_id][emoji_id])
    return role_messages

def matchemoji(all_emojis_func, emoji_id):
    '''(ReactionCommand, str) -> discord.Emoji or chr
    matches the emoji's id with the Discord emoji '''
    #return self.emoji==None or self.emoji==reaction.emoji or self.emoji==reaction.emoji.id
    if all_emojis_func == None:
        return
    if str(emoji_id) == emoji_id:
        return emoji_id
    for e in all_emojis_func():
        try:
            if e.id == emoji_id:
                return e
        except:
            if str(e) == emoji_id:
                return e
    # print("Fuck")
