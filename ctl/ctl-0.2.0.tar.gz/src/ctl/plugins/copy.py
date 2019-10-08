from __future__ import absolute_import

import os
import shutil
import re

import confu.schema
import ctl

from ctl.plugins.walk_dir import WalkDirPlugin, WalkDirPluginConfig


class CopyPluginConfig(WalkDirPluginConfig):
    copy_metadata = confu.schema.Bool(
        "copy_metadata", default=True, help="Copy file metadata"
    )


@ctl.plugin.register("copy")
class CopyPlugin(WalkDirPlugin):

    """ copy files """

    class ConfigSchema(ctl.plugins.PluginBase.ConfigSchema):
        config = CopyPluginConfig("config")

    def prepare(self):
        super(CopyPlugin, self).prepare()
        self.requires_output = True
        self.debug_info["copied"] = []
        self.copy_metadata = self.get_config("copy_metadata")

    def process_file(self, path, dirpath):
        r = self.copy_file(path, dirpath)
        super(CopyPlugin, self).process_file(path, dirpath)
        return r

    def copy_file(self, path, dirpath):
        output_dir = os.path.dirname(self.output(path))
        self.log.info(self.output(path))

        self.debug_append("copied", self.output(path))

        if self.copy_metadata:
            shutil.copy2(self.source(path), self.output(path))
        else:
            shutil.copy(self.source(path), self.output(path))
