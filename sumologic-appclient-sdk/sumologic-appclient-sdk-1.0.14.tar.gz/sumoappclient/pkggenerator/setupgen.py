# -*- coding: future_fstrings -*-

import os
import shutil
import sys


if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, cur_dir)

from common.utils import get_normalized_path
from pkggenerator.base import PkgGenerator


class SetupGen(PkgGenerator):

    def __init__(self, configpath, *args, **kwargs):
        super(SetupGen, self).__init__(configpath, *args, **kwargs)

    def setup_env(self):
        self.remove_unwanted_files(self.project_dir)

    def generate_setup_files(self, target_folder):
        target_folder = get_normalized_path(target_folder)
        for filename in ["setup.py", "README.md", "MANIFEST.in"]:
            self.generate_file(os.path.join(self.RESOURCE_FOLDER, "setup", filename), self.deploy_config, os.path.join(target_folder, filename))
        for filename in ["LICENSE", "VERSION"]:
            shutil.copyfile(os.path.join(self.RESOURCE_FOLDER, "setup", filename), os.path.join(target_folder, filename))
