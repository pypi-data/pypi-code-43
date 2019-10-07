#!/usr/bin/env python
# coding=utf-8

from parapheur.parapheur import config
import os
from os import path as os_path

server=config.get("Parapheur", "server")
folder=config.get("Parapheur", "folder")
PATH = os_path.abspath(os_path.split(__file__)[0])
script = PATH + "/script/patch.sh"
print(script)

os.chmod(script, 0755)
script2 = script + " " + folder + " " + server
os.system(script2)