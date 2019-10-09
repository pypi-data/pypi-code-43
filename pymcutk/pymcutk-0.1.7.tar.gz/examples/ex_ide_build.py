"""
This example show how to use mcutk.apps to project.
"""
import os
import sys
import subprocess
import argparse

sys.path.append("./../")
from mcutk.apps import factory


parser = argparse.ArgumentParser()
parser.add_argument("-n", dest="name", help="app name")
parser.add_argument("-p", dest="project", help="project path")
args = parser.parse_args(sys.argv[1:])

# get app module
appmodule = factory(args.name)

# get instance by scaning the system
app = appmodule.APP.get_latest()

print app

if args.project:
    print args.project
    project = appmodule.Project(args.project)
    for tname in project.targets:
        logfile = os.path.join(os.path.dirname(args.project), tname + "_log.log")
        print "%s is building..."%tname
        print app.build_project(project, tname, logfile)




