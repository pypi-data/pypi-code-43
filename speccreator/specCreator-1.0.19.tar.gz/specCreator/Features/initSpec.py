#!/usr/bin/env python
# -*- coding=utf-8 -*-


import sys
import os
from Tools.result import Result
from Tools.formatter import Formatter
from Tools.fileHandle import FileHandle
from Tools.shellCommand import Shell
from Tools.arguments import Arguments
from Tools.constant import *
from Tools.commonFuncs import *


class InitSpec(object):
    __instance = None

    def __init__(self):
        self.formatter = Formatter.instance()
        self.result = Result.instance()
        self.fileHandle = FileHandle.instance()
        self.shell = Shell.instance()
        self.arguments = Arguments.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = InitSpec()
        return cls.__instance

    # TODO 重复修改问题
    def supportBinary(self):
        if not self.fileHandle.file_exist(Arguments.instance().projectPath):
            self.result.returnError("没找到工程目录")
        os.chdir(self.arguments.projectPath)
        projectPath = self.arguments.projectPath
        podName = self.arguments.podName
        subPackage = self.arguments.subPackage
        originSpecPath = projectPath + "/" + podName + ".podspec"
        content = self.fileHandle.readFile(originSpecPath)
        sourceList = matchList("(s.source_files += +[\'|\"].*?[\'|\"])", content)
        publicHeaderList = matchList("(s.public_header_files += +[\"|\'].*?[\"|\'])", content)
        replaceContent = ""
        if sourceList:
            if publicHeaderList:
                replaceContent = content.replace(publicHeaderList[0], "", 1)
            sourceKey = sourceList[0]
            self.formatter.format_info("即将替换" + sourceKey)
            if subPackage:
                replaceContent = replaceContent.replace(sourceKey, packageBySubspec, 1)
            else:
                replaceContent = replaceContent.replace(sourceKey, noSubSpec, 1)
        else:
            self.result.returnError("错误，没有找到关键字source_files ，可能已经完成替换或者其他的未知错误")
        self.fileHandle.writeToFile(replaceContent, originSpecPath)
        self.formatter.format_info(podName + "支持源码和二进制切换成功：")

