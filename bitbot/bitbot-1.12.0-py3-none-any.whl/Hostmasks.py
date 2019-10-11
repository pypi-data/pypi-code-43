import typing
from src import IRCBot, IRCServer

class Hostmasks(object):
    def __init__(self, bot: IRCBot, server: IRCServer):
        self.bot = bot
        self.server = server

    def get_all(self):
        return bot.database.hostmask_settings.get_hostmasks(self.server.id)

    def for_user(self, user: IRCUser.User) -> typing.List[Hostmask]:
        hostmasks = []
        user_hostmask = user.hostmask()
        for hostmask in self.get_all():
            if utils.irc.hostmask_match(user_hostmask, hostmask):
                hostmasks.append(hostmask)
        return hostmasks
