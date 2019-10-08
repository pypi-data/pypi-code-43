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


class Init(object):
    __instance = None


    def __init__(self):
        self.formatter = Formatter.instance()
        self.result = Result.instance()
        self.tips = Tips.instance()
        self.fileHandle = FileHandle.instance()
        self.shell = Shell.instance()
        self.arguments = Arguments.instance()
        self.cocoaPodsTool = CocoapodsTool.instance()
        self.initSpec = InitSpec.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = Init()
        return cls.__instance

    def create(self):
        """
        创建一个组件库。
        """
        projectPath = self.arguments.projectPath
        projectName = self.arguments.podName
        projectParentDict = self.arguments.projectParentDict
        user = self.arguments.user
        if not self.fileHandle.file_exist(projectParentDict):
            self.formatter.format_warning("父目录" + projectParentDict + "不存在，即将创建此目录")
            self.shell.excommand_until_done(r"sudo mkdir -p " + projectParentDict)
        os.chdir(projectParentDict)
        if self.fileHandle.file_exist(projectPath):
            self.result.returnError("文件已经存在，请确保这个工程是第一次初始化")
        success = self.cocoaPodsTool.libCreate()
        if not success:
            self.result.returnError("模板初始化失败")
        self.formatter.format_print("切换到工程目录")
        # self.shell.excommand_until_done("chmod +x " + projectName)
        os.chdir(projectPath)
        # TODO 去掉耦合
        gerritUrl = "ssh://" + user + "@gerrit.lianjia.com:29418/mobile_ios/" + projectName
        self.formatter.format_print("项目gerrit地址是：" + gerritUrl)
        self.shell.excommand_until_done("git remote add origin " + gerritUrl)
        changeIDHookUrl = user + "@gerrit.lianjia.com:hooks/commit-msg"
        self.formatter.format_print("拉取gerrit的产生changID的脚本")
        self.shell.excommand_until_done(
            "gitdir=$(git rev-parse --git-dir); scp -p -P 29418 " + changeIDHookUrl + " ${gitdir}/hooks/")
        self.formatter.format_print("添加提交脚本review.sh")
        self.fileHandle.writeToFile(reviewInfo, projectPath + "/review.sh")
        if self.fileHandle.file_exist("review.sh"):
            self.formatter.format_print("给提交脚本设置运行权限")
            self.shell.excommand_until_done("chmod +x review.sh")
        self.formatter.format_print("添加文档更新文件VersionHistory.md")
        self.shell.excommand_until_done("touch VersionHistory.md")
        # 更改podSpec文件
        self.initSpec.supportBinary()
        self.addIgnoreFile()
        self.formatter.format_print("初始化git相关")
        self.shell.excommand_until_done("git add .")
        self.shell.excommand_until_done("git commit --amend --no-edit")

        "切换分支因为涉及到需要远端先创建分支，一般没有push权限"
        # formatPrint("创建develop分支并同步到远端")
        # excommandUntilDone("git branch develop")
        # excommandUntilDone("git push origin develop")
        # formatPrint("切换到develop 分支")
        # excommandUntilDone("git checkout develop")
        self.formatter.format_info("组件创建成功：")

    def addIgnoreFile(self):
        self.formatter.format_info("正在处理 git ignore ")
        if not self.fileHandle.file_exist(".gitignore"):
            self.shell.excommand_until_done("touch .gitignore")
        self.fileHandle.writeToFile(ignoreFileString, ".gitignore")