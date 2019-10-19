"""
The sys command to manage the cmd5 distribution
"""
from __future__ import print_function

from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command

from cloudmesh.sys.manage import Command, Git, Version
import shutil
import glob
from cloudmesh.common.util import path_expand
import os

class SysCommand(PluginCommand):
    """
    The system command
    """

    # noinspection PyUnusedLocal
    @command
    def do_sys(self, args, arguments):
        """
        ::

          Usage:
            sys upload
            sys commit MESSAGE
            sys command generate NAME [.]
            sys version VERSION

          This command does some useful things.

          Arguments:
            MESSAGE   the message to commit 
            NAME      the command to generate
            VERSION   the version number

          Options:
            -f      specify the file

          Description:      
            cms sys command generate NAME

                
                When you execute this command it
                will generate a  directory tree for a command
                with the name

                cloudmesh-NAME

                To install the command you need to

                cd cloudmesh-NAME
                pip install -e .

                or

                pip install .

            cms sys command generate NAME .

                the code will be installed in the current directory. This is
                helpful, if you already are in adirectory fof the name
                cloudmesh-NAME, e.g. if you already created it in github and
                like to add a command in that github directory.

            The commands 'version', 'commit' and 'upload'
            are only to be used by Gregor.        
    
            cms version
                The version command adds a new version to the 
                VERSION file for cmd5, common, and sys.
                This helps to keep the versions aligned across 
                these modules.
            
            cms commit
                The commit  command adds a new version and commits

            cms upload
                The upload command uploads the new version to pypi

            
        """
        print(arguments)

        dot = arguments["."]

        if arguments.commit:

            msg = arguments.MESSAGE
            Git.commit(msg)

        elif arguments.upload:

            Git.upload()

        elif arguments.readme and arguments.generate:

            name = arguments.NAME
            Command.generate(name)

        elif arguments.command and arguments.generate:

            name = arguments.NAME
            Command.generate(name)

            if dot:
                for file in ["LICENSE",
                             ".bumpversion.cfg",
                             ".gitignore",
                             "requirements.txt",
                             "Makefile"]:
                    try:
                        os.remove(file)
                    except:
                        pass

                for entry in glob.glob("cloudmesh-{name}/**".format(name=name)):
                    shutil.move(entry, path_expand("."))
                for entry in glob.glob("cloudmesh-{name}/.*".format(name=name)):
                    shutil.move(entry, path_expand("."))
                shutil.rmtree("cloudmesh-{name}".format(name=name))


        elif arguments.version:

            version = arguments.VERSION
            Version.set(version)

