import os
import ctl
import confu.schema
from ctl import plugin
from ctl.plugins.log_user import LogUserPlugin


class LogGitConfig(LogUserPlugin.ConfigSchema.config):
    git = confu.schema.Str(
        "git", help="a `git` type plugin to use to obtain uuid and version"
    )


@ctl.plugin.register("log_git")
class LogGitPlugin(LogUserPlugin):
    class ConfigSchema(LogUserPlugin.ConfigSchema):
        config = LogGitConfig

    default_config = confu.generator.generate(LogGitConfig)

    def init(self):
        self.git = plugin._instance.get(self.config.get("git"))

        for logger in self.config.get("loggers", []):
            filepath = logger.get("file")
            if filepath and filepath[0] != "/":
                logger["file"] = os.path.join(self.git.checkout_path, filepath)

        super(LogGitPlugin, self).init()

    def apply(self, message, level):
        message = super(LogGitPlugin, self).apply(message)
        return "{uuid}:{version} {message}".format(
            uuid=self.git.uuid, version=self.git.version, message=message
        )
