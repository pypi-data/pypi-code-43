from __future__ import absolute_import, division, print_function

import sys
import os
import ctl
import ctl.config
import subprocess
import select
import confu.schema


from ctl.auth import expose


class CommandPluginConfig(confu.schema.Schema):
    """
    configuration schema for command plugin
    """

    command = confu.schema.List(
        item=confu.schema.Str("command.item"),
        help="List of shell commands to run",
        cli=False,
    )
    arguments = confu.schema.List(item=ctl.config.ArgparseSchema(), cli=False)
    env = confu.schema.Dict(item=confu.schema.Str(), default={}, cli=False)
    shell = confu.schema.Bool(
        default=False, cli=False, help="run subprocess in shell mode"
    )
    working_dir = confu.schema.Directory(
        default=None,
        blank=True,
        help="set a working directory before " "running the commands",
    )


@ctl.plugin.register("command")
class CommandPlugin(ctl.plugins.ExecutablePlugin):
    """
    runs a command
    """

    class ConfigSchema(ctl.plugins.PluginBase.ConfigSchema):
        config = CommandPluginConfig("config")

    description = "run a command"

    @classmethod
    def add_arguments(cls, parser, plugin_config):
        ctl.config.ArgparseSchema().add_many_to_parser(
            parser, plugin_config.get("arguments")
        )

    def prepare(self, **kwargs):
        self.env = os.environ.copy()
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.env.update(**(self.get_config("env") or {}))
        self.cwd = self.get_config("working_dir")
        self.shell = self.get_config("shell")

    # namespace will be built using the name of the
    # plugin instance
    #
    # required permissions will be obtained from `permissions` key
    # in the plugin's config, and default to `r` if not specified
    @expose("ctl.{plugin_name}")
    def execute(self, **kwargs):
        super(CommandPlugin, self).execute(**kwargs)
        command = self.get_config("command")
        self._run_commands(command, **kwargs)

    def _run_commands(self, command, **kwargs):
        for cmd in command:
            cmd = self.render_tmpl(cmd, kwargs)
            self.log.debug("running command: {}".format(cmd))
            rc = self._exec(cmd)
            self.log.debug("done with {}, returned {}".format(cmd, rc))
            if rc:
                self.log.error("command {} failed with {}".format(cmd, rc))
                return False

    def _exec(self, command):
        chunk_size = 4096

        popen_kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "shell": self.shell,
            "env": self.env,
            "cwd": self.cwd,
        }

        proc = subprocess.Popen(command, **popen_kwargs)
        stdout = []
        stderr = []

        with proc.stdout:
            for line in iter(proc.stdout.readline, b""):
                line = line.decode("utf-8")
                stdout.append(line)

        with proc.stderr:
            for line in iter(proc.stderr.readline, b""):
                line = line.decode("utf-8")
                stderr.append(line)

        for line in stdout:
            self.stdout.write(u"{}".format(line))

        for line in stderr:
            self.stderr.write(u"{}".format(line))

        return proc.returncode
