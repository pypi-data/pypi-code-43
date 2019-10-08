from __future__ import absolute_import, division, print_function

import pluginmgr.config
import confu.schema
import ctl

from ctl.log import Log
from ctl.events import common_events
from ctl.exceptions import ConfigError, UsageError, OperationNotExposed

__all__ = ["command", "config"]


class PluginConfigSchema(confu.schema.Schema):
    """
    configuration schema for plugin base
    """

    name = confu.schema.Str("name", default="", help="Plugin name")
    type = confu.schema.Str("type", help="Plugin type")
    description = confu.schema.Str(
        "description", default="", blank=True, help="description of plugin"
    )

    # we also want to create an empty sub schema for `config` key
    # this should be overwritten in the classes extending this plugin
    config = confu.schema.Schema("config", help="plugin specific config")


class PluginBase(pluginmgr.config.PluginBase):
    """
    Base plugin class

    Initializes:

    - `self.config` as plugins config
    - `self.log` as a ctl.log.Log instance
    - `self.ctl` as a reference to the main ctl object

    """

    ConfigSchema = PluginConfigSchema

    #    def init(self):
    #        pass

    def __init__(self, plugin_config, ctx, *args, **kwargs):
        self.ctl = ctx
        self.pluginmgr_config = plugin_config

        # TODO: this can be removed once confu can have proxy schemas
        # apply defaults
        schema = self.ConfigSchema()
        confu.schema.apply_defaults(schema, plugin_config)

        self.config = plugin_config.get("config", {})

        self.args = args
        self.kwargs = kwargs
        self.init()
        self.attach_events(self.pluginmgr_config.get("events", {}))

    @property
    def plugin_name(self):
        return self.pluginmgr_config.get("name")

    def attach_events(self, events):
        """
        attach plugin events
        """
        for event_name, event_config in events.items():
            self.attach_event(event_name, event_config)

    def attach_event(self, name, config):
        for handler_name, instances in config.items():
            handler = getattr(self, handler_name, None)

            if not handler:
                raise ValueError(
                    "Tried to attach unknown plugin method `{}` to event `{}`".format(
                        handler_name, name
                    )
                )

            def callback(events, handler=handler, *args, **kwargs):
                if not instances:
                    handler()
                    return
                for params in instances:
                    handler(**params)

            common_events.on(name, callback)

    def init(self):
        """
        called after the plugin is initialized, plugin may define this for any
        other initialization code
        """
        pass

    @classmethod
    def option_list(cls):
        return []

    @classmethod
    def add_arguments(cls, parser, plugin_config):
        pass

    @property
    def log(self):
        if not getattr(self, "_logger", None):
            self._logger = Log("ctl.plugins.{}".format(self.plugin_type))
        return self._logger

    def call(self, *args, **kwargs):
        print("command call ")

    def other_plugin(self, name):
        """
        return plugin instance by name
        convenience function as plugins often reference other
        plugins
        """

        if name == "self":
            return self

        other = ctl.plugin._instance.get(name)
        if not other:
            raise KeyError("Plugin instance with name `{}` does not exist".format(name))
        return other

    def render_tmpl(self, content, env=None):
        tmpl = self.ctl.ctx.tmpl

        if not tmpl.get("engine"):
            return content

        if env:
            _env = {"kwargs": env}
            _env.update(tmpl["env"])
            env = _env
        else:
            env = tmpl["env"]
        return tmpl["engine"]._render_str_to_str(content, env)

    def get_op(self, op):
        if not op:
            # TODO UsageError
            raise ValueError("operation not defined")
        elif not callable(getattr(self, op, None)):
            # TODO Usage Error
            raise ValueError("invalid operation")

        fn = getattr(self, op)

        if not getattr(fn, "exposed", False):
            raise OperationNotExposed(op)

        return fn


class ExecutablePlugin(PluginBase):

    """
    Base plugin class for CLI executable plugins
    """

    def prepare(self, **kwargs):
        """
        extend and use this to set instance properties
        and prepare for execution
        """
        pass

    def execute(self, **kwargs):
        """
        Extended execute function should call this to make
        sure cli parameters are set and prepare() is called
        """
        self.kwargs = kwargs
        self.prepare()

    def get_config(self, name):
        """
        Retrieve configuration properties from cli parameters
        and plugin config.

        For a property that exist as both a cli argument and
        a config property the cli argument takes priority, but
        it's default value will be informed by the configuration
        property - so you get to have your cake, and eat it too.

        Argument(s):

            - name(str): config key

        Returns:

            - config / cli parameter property

        """

        return self.kwargs.get(name, self.config.get(name))


# TODO PluginStageBase
