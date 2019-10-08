from __future__ import absolute_import

import os
import shutil
import re

import confu.schema
import ctl


class MatchConfig(confu.schema.Schema):

    # TODO: Regex Attribute

    pattern = confu.schema.Str()
    plugin = confu.schema.Str(default="self")
    action = confu.schema.Str()


class WalkDirPluginConfig(confu.schema.Schema):

    # TODO: source should be a Directory attribute, but as it stands sometimes
    # the directory might be missing during validation, and may be created during
    # runtime by another plugin.

    source = confu.schema.Str(help="source directory")
    output = confu.schema.Str(help="output directory")

    walk_dirs = confu.schema.List(
        item=confu.schema.Str(),
        cli=False,
        help="list of subdirectories to walk and process files in",
    )

    ignore = confu.schema.List(item=confu.schema.Str(), cli=False)

    process = confu.schema.List(item=MatchConfig(), cli=False)

    debug = confu.schema.Bool(default=False)
    skip_dotfiles = confu.schema.Bool(default=True, help="Skip dot files")


@ctl.plugin.register("walk_dir")
class WalkDirPlugin(ctl.plugins.ExecutablePlugin):
    """ walk directories and process files """

    class ConfigSchema(ctl.plugins.PluginBase.ConfigSchema):
        config = WalkDirPluginConfig("config")

    #    @classmethod
    #    def add_arguments(cls, parser, plugin_config):
    #        parser.add_argument("--source", type=str, help="source dir")
    #        parser.add_argument("--output", type=str, help="output dir")

    def prepare(self, **kwargs):
        self.debug = self.config.get("debug")
        self.debug_info = {"files": [], "processed": [], "mkdir": []}

        self.requires_output = False
        self._source = self.get_config("source")
        self._output = self.get_config("output")
        self.walk_dirs = self.get_config("walk_dirs")
        self.skip_dotfiles = self.get_config("skip_dotfiles")

        self.log.info("Skip dotfiles: {}".format(self.skip_dotfiles))

        if not os.path.exists(self._output):
            os.makedirs(self._output)

    def source(self, path=None):
        if path:
            return os.path.join(self._source, path)
        return self._source

    def output(self, path=None):
        if not self._output:
            return path
        if path:
            return os.path.join(self._output, path)
        return self._output

    def execute(self, **kwargs):

        super(WalkDirPlugin, self).execute(**kwargs)

        if not self._output and self.requires_output:
            raise ValueError("No output directory specified")

        if not self._source:
            raise ValueError("No source directory specified")

        if self._output:
            self._output = self.render_tmpl(self._output)

        self._source = self.render_tmpl(self._source)

        self.source_regex = r"^{}/".format(self.source())

        self.process_files()

    def process_files(self):
        for subdir in self.walk_dirs:
            for dirpath, dirnames, filenames in os.walk(self.source(subdir)):
                path = re.sub(self.source_regex, "", dirpath)

                for filepath, filename in [
                    (os.path.join(path, _f), _f) for _f in filenames
                ]:

                    if self.skip_dotfiles and filename[0] == ".":
                        continue

                    if not self.ignored(filepath, path):
                        self.prepare_file(filepath, path)
                        self.process_file(filepath, path)

    def prepare_file(self, path, dirpath):
        output_dir = os.path.dirname(self.output(path))
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
            self.debug_append("mkdir", output_dir)

    def process_file(self, path, dirpath):

        self.debug_append("files", path)

        for process_config in self.get_config("process"):
            plugin = self.other_plugin(process_config.get("plugin"))
            action = process_config.get("action")
            pattern = process_config.get("pattern")
            if re.search(pattern, path) is not None:
                fn = getattr(plugin, action)
                r = fn(source=self.source(path), output=self.output(path))
                self.debug_append(
                    "processed",
                    {
                        "plugin": process_config.get("plugin"),
                        "source": self.source(path),
                        "output": self.output(path),
                    },
                )

    def ignored(self, path, dirpath):
        for pattern in self.get_config("ignore"):
            if re.search(pattern, path) is not None:
                return True

    def debug_append(self, typ, data):
        if self.debug:
            self.debug_info[typ].append(data)
