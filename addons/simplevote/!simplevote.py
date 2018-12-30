from libs import reaction

YES_EMOJI = "yes_emoji"
NO_EMOJI = "no_emoji"

class Reaction(reaction.Config, reaction.Dummy):
    '''No, *you're* a dummy reaction-command'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.public_namespace.vote_dict = dict() # this is a dict of dicts; dict-ception
        self.public_namespace.yes_emoji = self.config[YES_EMOJI]
        self.public_namespace.no_emoji = self.config[NO_EMOJI]
