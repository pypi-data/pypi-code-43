"""
Managing the cmd5 system installation and package distribution
"""
from __future__ import print_function

import os
import shutil
from distutils.dir_util import copy_tree
from pprint import pprint

from cloudmesh.common.util import readfile, writefile
from cloudmesh.common.util import banner
from cloudmesh.common.util import writefile
from cloudmesh.common.console import Console
import sys
from cloudmesh.common.Shell import Shell
from pathlib import Path
import platform
import stat

class Command(object):
    """
    Class to generate cmd5 command templates
    """

    @classmethod
    def generate(cls, name):
        """
        Generate a command template with the given name
        :param name: the name of the command
        :return: 
        """

        data = {
            "command": name,
            "package": "cloudmesh-{}".format(name),
            "Command": name.capitalize()
        }

        pprint(data)

        # os.system("rm -rf  cloudmesh-gregor")
        # noinspection PyUnusedLocal,PyBroadException
        try:
            shutil.rmtree("cloudmesh-bar")
        except:
            pass
        try:
            os.system("git clone https://github.com/cloudmesh/cloudmesh-bar")
        except Exception as e:
            pass


        if os.path.isdir("{package}/cloudmesh/{command}".format(**data)):
            Console.error('The command directory "{package}/cloudmesh/{command}" already exists'.format(**data))
            return ""

        def replace_in_file(filename, old_text, new_text):
            content = readfile(filename)
            content = content.replace(old_text, new_text)
            writefile(filename, content)

        def delete(path, pattern):
            files = Path(path).glob(pattern)
            for file in files:
                file.unlink()

        for pattern in ["*.zip",
                        "*.egg-info",
                        "*.eggs",
                        "build",
                        "dist",
                        ".tox",
                        "*.whl",
                        "**/__pycache__",
                        "**/*.pyc",
                        "**/*.pye"]:
            delete("./cloudmesh-bar/", pattern)

        #
        # os.system("cd cloudmesh-bar; make clean")
        #
        # clean = """
        # rm -rf cloudmesh-bar/*.zip
        # rm -rf cloudmesh-bar/*.egg-info
        # rm -rf cloudmesh-bar/*.eggs
        # rm -rf cloudmesh-bar/docs/build
        # rm -rf cloudmesh-bar/build
        # rm -rf cloudmesh-bar/dist
        # rm -rf cloudmesh-bar/.tox
        # rm -f cloudmesh-bar/*.whl
        # find cloudmesh-bar -type d -name __pycache__ -delete
        # find cloudmesh-bar -name '*.pyc' -delete
        # find cloudmesh-bar -name '*.pye' -delete
        # """
        # for line in clean.splitlines():
        #     try:
        #         r = os.system(line.strip())
        #     except:
        #         pass
        #     print (line.strip())

        path = Path("cloudmesh-bar/.git".format(**data)).resolve()
        Shell.rmdir(path)

        copy_tree("cloudmesh-bar", "{package}".format(**data))

        path = Path("{package}/.git".format(**data)).resolve()
        Shell.rmdir(path)

        replace_in_file("{package}/setup.py".format(**data),
                        "bar",
                        "{command}".format(**data) )


        os.rename("{package}/cloudmesh/bar/command/bar.py".format(**data),
                  "{package}/cloudmesh/bar/command/{command}.py".format(**data))
        os.rename("{package}/cloudmesh/bar".format(**data),
                  "{package}/cloudmesh/{command}".format(**data))

        shutil.rmtree('{package}/cloudmesh/foo'.format(**data))
        shutil.rmtree('{package}/cloudmesh/plugin'.format(**data))

        replace_in_file("{package}/cloudmesh/{command}/command/{command}.py".format(**data),
                        "Bar",
                        "{Command}".format(**data))

        replace_in_file("{package}/cloudmesh/{command}/command/{command}.py".format(**data),
                        "bar",
                        "{command}".format(**data))

        replace_in_file("{package}/Makefile".format(**data),
                        "bar",
                        "{command}".format(**data) )

        delete("{package}".format(**data), "Makefilee")
        delete("{package}".format(**data), "setup.pye")

        shutil.rmtree("cloudmesh-bar")

class Git(object):
    """
    Git management for the preparation to upload the code to pypi
    """

    pypis = ["cloudmesh-common",
             "cloudmesh-cmd5",
             "cloudmesh-sys",
             "cloudmesh-comet",
             "cloudmesh-openapi"]
    commits = pypis + ["cloudmesh-bar"]
    # , "cloudmesh-rest"]
    # "cloudmesh-robot"]

    @classmethod
    def upload(cls):
        """
        upload the code to pypi
        :return: 
        """

        banner("CREATE DIST")
        for p in cls.pypis:
            try:
                os.system("cd {}; make dist".format(p))
            except Exception as e:
                Console.error("can not create dist" + p)
                print(e)

        banner("UPLOAD TO PYPI")
        for p in cls.pypis:
            try:
                os.system("cd {}; make upload".format(p))
            except Exception as e:
                Console.error("can upload" + p)
                print(e)

    @classmethod
    def commit(cls, msg):
        """
        commit the current code to git
        :param msg: 
        :return: 
        """

        banner("COMMIT " + msg)
        for p in cls.commits:
            banner("repo " + p)
            os.system('cd {}; git commit -a -m "{}"'.format(p, msg))
            os.system('cd {}; git push'.format(p))


class Version(object):
    """
    set the version number of all base packages
    """

    @classmethod
    def set(cls, version):
        """
        set the version number
        :param version: the version as text string
        :return: 
        """
        for repo in Git.commits:
            print(repo, "->", version)
            writefile(os.path.join(repo, "VERSION"), version)
