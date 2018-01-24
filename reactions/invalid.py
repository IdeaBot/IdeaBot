from reactions import reactioncommand as rc

class InvalidCommand(rc.AdminReactionAddCommand, rc.AdminReactionRemoveCommand):
    def matches(self, reaction, user):
        return True
    def action(self, reaction, user, client):
        pass
