#!/usr/bin/env python
# -*- coding=utf-8 -*-


import sys
import os
import importlib
from Tools.tips import Tips
from Tools.result import Result
from Tools.formatter import Formatter
from Tools.fileHandle import FileHandle
from Tools.shellCommand import Shell
from Tools.arguments import Arguments
from Tools.cocoapodsTool import CocoapodsTool
from Tools.constant import *
from initSpec import InitSpec
from Tools.resultModel import ResultModel


class Check(object):
    __instance = None


    def __init__(self):
        self.formatter = Formatter.instance()
        self.result = Result.instance()
        self.tips = Tips.instance()
        self.fileHandle = FileHandle.instance()
        self.shell = Shell.instance()
        self.arguments = Arguments.instance()
        self.cocoaPodsTool = CocoapodsTool.instance()
        self.podspec = InitSpec.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = Check()
        return cls.__instance


    def check(self):
        os.chdir(self.arguments.projectPath)
        self.arguments.branch, self.arguments.commitId = self.gitTool.currentBranchAndCommitID()
        self.libLint()

    def libLint(self):
        self.cocoaPodsTool.libLint()
        ResultModel.instance().resultDict["checkSuccess"] = True
        self.formatter.format_info("组件check通过")