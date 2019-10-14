#!/usr/bin/env python3
"""
Python Package Maker. Creates an empty template of a ready-made python project.
"""
import argparse
import json
import os
import shutil

from string import Template


class Pak():
    def __init__(self):
        self.parse_args()

    def parse_args(self):
        """gets basic args from the end-user"""
        parser = argparse.ArgumentParser(description=__doc__,)

        parser.add_argument(
            "-c", "--config",
            default=os.environ.get('PAKCONFIG'),
            type=argparse.FileType('a+'),
            help="Optional config; should be a pakconfig.json file.")
        parser.add_argument(
            "-o", "--override",
            default=False,
            action="store_true",
            help="Whether or not to override existing files. Default is False.")

        self.args, _ = parser.parse_known_args()

    def _get_responses(self):
        """asks questions to the user for missing info not found in config"""
        pakfile = self.args.config or os.path.join(os.getcwd(), 'pakconfig.json')
        with open(pakfile, 'a+') as json_file:
            # move file pointer to the front of the file; opening with a+
            # allows reading from an empty file if the file doesn't already exist
            # and also writing to that same file. r+ would error if file not found
            # TODO: would `w+` achieve desired result?
            json_file.seek(0)
            try:
                self.config = json.load(json_file)
            except json.decoder.JSONDecodeError:
                # if json file is malformed or non-existant
                self.config = {}

            print("Answer some questions! Hit enter for defaults, "
                  "and pass in an empty string for a null value.")

            # default outputdir to current dir if not set
            if 'outputdir' not in self.config:
                self.config['outputdir'] = os.getcwd()

            options = [
                ("outputdir", "New app directory: "),
                ("app", "App name: "),
                ("description", "App description: "),
                ("author", "App author: "),
                ("email", "App email: "),
                ("url", "App url: "),
                ("package_data", "App package data: "),
            ]
            for option in options:
                question = option[1]
                # if option found, display default info
                if option[0] in self.config:
                    question = question[:question.find(':')] + "[{}]".format(
                        self.config[option[0]]) + question[question.find(':'):]

                self.config[option[0]] = input(question) or self.config.get(option[0])

            json_file.seek(0)
            json_file.truncate()
            json.dump(self.config, json_file, indent=2)

    def create_package(self):
        """iterates over the templates folder, uses user responses to
           create python package
        """
        self._get_responses()

        # create base app folders
        basedir = os.path.join(self.config['outputdir'], self.config['app'])
        appdir = os.path.join(basedir, self.config['app'])
        os.makedirs(appdir, exist_ok=True)

        # iterate over templates to generate new files
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        for f in os.listdir(template_dir):
            template_file = os.path.join(template_dir, f)
            # ignore folders like __pycache__
            if os.path.isfile(template_file):
                with open(template_file, 'r') as template:
                    out = Template(template.read()).safe_substitute(**self.config)

                    # files that go in the top-level dir
                    if f in ['Makefile',
                             'MANIFEST.in',
                             'README.md',
                             'requirements-dev.txt',
                             'setup.cfg',
                             'setup.py',
                             'tox.ini',
                             'versioneer.py',
                             'LICENSE']:
                        newfile = os.path.join(basedir, f)
                    else:
                        # files that go in the app/app dir
                        newfile = os.path.join(appdir, f)

                    # preserve any existing files if override flag is false
                    if not os.path.exists(newfile) or self.args.override:
                        with open(newfile, 'w') as new:
                            new.write(out)

        # include any extra files/dirs in new project
        for f in self.config['package_data'].split(','):
            if not os.path.isabs(f):
                f = os.path.join(os.getcwd(), f)
            newpath = os.path.join(appdir, os.path.basename(f))

            # NOTE: this will ignore dirs already copied even if the new dir contains new stuff
            # this is due to copytree's recursiveness and not wanting to override any existing files
            if os.path.exists(f) and (not os.path.exists(newpath) or self.args.override):
                cmd = shutil.copy if os.path.isfile(f) else shutil.copytree
                # shutil.copytree breaks on existing folders so delete old folder first
                if os.path.exists(newpath):
                    shutil.rmtree(newpath)
                cmd(f, newpath)

        # in order to create pak, need to copy pak to the main.py file
        if self.config['app'] == 'pak':
            main_file = os.path.join(appdir, 'main.py')
            shutil.copy(__file__, main_file)
            os.chmod(main_file, 0o644)


def main():
    """Main entrypoint into pak"""
    Pak().create_package()


if __name__ == '__main__':
    main()
