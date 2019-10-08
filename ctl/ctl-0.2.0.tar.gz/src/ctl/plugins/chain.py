from __future__ import absolute_import
import argparse

import copy
import confu.schema
import ctl
import ctl.config


class ChainActionConfig(confu.schema.Schema):
    name = confu.schema.Str(
        default="execute", help="call this action on the plugin instance"
    )
    arguments = confu.schema.Schema(
        item=confu.schema.Str(), help="arguments to pass to the plugin's " "execute"
    )


class ChainConfig(confu.schema.Schema):
    stage = confu.schema.Str(help="user friendly name of the stage in the chain")
    plugin = confu.schema.Str(help="plugin instance name")
    action = ChainActionConfig()


class ChainPluginConfig(confu.schema.Schema):
    arguments = confu.schema.List(item=ctl.config.ArgparseSchema(), cli=False)
    chain = confu.schema.List(item=ChainConfig(), cli=False)
    vars = confu.schema.Dict(item=confu.schema.Str(blank=True), cli=False)


@ctl.plugin.register("chain")
class ChainPlugin(ctl.plugins.ExecutablePlugin):

    """ chain execute other plugins """

    class ConfigSchema(ctl.plugins.PluginBase.ConfigSchema):
        config = ChainPluginConfig("config")

    @classmethod
    def expose_vars(cls, env, plugin_config):
        env.update(plugin_config.get("vars"))

    @classmethod
    def add_arguments(cls, parser, plugin_config):
        parser.add_argument("--end", type=str, help="stop at this stage")
        parser.add_argument("--start", type=str, help="start at this stage")
        ctl.config.ArgparseSchema().add_many_to_parser(
            parser, plugin_config.get("arguments")
        )

    def execute(self, **kwargs):
        super(ChainPlugin, self).execute(**kwargs)
        self.chain = chain = self.get_config("chain")
        self.end = kwargs.get("end")
        self.start = kwargs.get("start")
        self.execute_chain(chain)

    def execute_chain(self, chain):

        self.validate_stage(self.end)
        self.validate_stage(self.start)

        total = len(chain)
        num = 1
        started = True

        if self.start:
            started = False

        for stage in chain:
            if self.start == stage["stage"]:
                started = True
            if not started:
                self.log.info("skip {}".format(stage["stage"]))
                continue
            self.execute_stage(stage, num, total)
            num += 1
            if self.end == stage["stage"]:
                self.log.info("end {}".format(self.end))
                return

        self.log.info("completed chain `{}`".format(self.plugin_name))

    def execute_stage(self, stage, num=1, total=1):
        self.log.info(
            "exec {stage} [{num}/{total}]".format(s=self, num=num, total=total, **stage)
        )
        plugin = self.other_plugin(stage["plugin"])
        fn = getattr(plugin, stage["action"]["name"], None)
        if not callable(fn):
            raise AttributeError(
                "Action `{action.name}` does not exist in plugin `{plugin}".format(
                    **stage
                )
            )

        kwargs = {}
        for name, value in stage["action"].get("arguments", {}).items():
            kwargs[name] = self.render_tmpl(value)

        fn(**kwargs)

    def validate_stage(self, name):
        if not name:
            return

        for stage in self.chain:
            if stage.get("stage") == name:
                return
        raise ValueError("Invalid stage speciefied - does not exist: {}".format(name))
