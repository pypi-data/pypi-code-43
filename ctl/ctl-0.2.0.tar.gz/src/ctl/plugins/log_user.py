import pwd
import os
import ctl
from ctl import plugin
from ctl.plugins.log import LogPlugin


@ctl.plugin.register("log_user")
class LogUserPlugin(LogPlugin):
    def init(self):
        super(LogUserPlugin, self).init()
        self.username = pwd.getpwuid(os.getuid()).pw_name

    def apply(self, message):
        prefix = "{who}".format(who=self.username)
        return "{prefix} - {message}".format(prefix=prefix, message=message)
