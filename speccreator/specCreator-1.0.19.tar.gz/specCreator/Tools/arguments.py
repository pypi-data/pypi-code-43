#!/usr/bin/env python
# -*- coding=utf-8 -*-

import sys
import os
import getopt
import json
from commonFuncs import *
from constant import *
from formatter import Formatter
from result import Result
from fileHandle import FileHandle
from tips import Tips
from shellCommand import Shell

class Arguments(object):
    __instance = None

    def __init__(self):
        self.formatter = Formatter.instance()
        self.result = Result.instance()
        self.fileHandle = FileHandle.instance()
        self.tips = Tips.instance()
        self.shell = Shell.instance()
        self._initArguments()
        self._arguments()
        self._checkArgues()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = Arguments()
        return cls.__instance

    def _initArguments(self):

        # 调试信息
        # 调试信息要不要打开
        self.debug = False
        # 白名单信息，
        self.whiteListPath = ""

        # 项目信息
        # 用户名
        self.user = ""
        # 工程目录
        self.projectPath = ""
        # pod 名字
        self.podName = ""
        # 分支
        self.branch = ""
        # 将要打的版本
        self.version = ""
        # 将要打的commitID
        self.commitId = ""
        # pod库是否按subspec分别进行打包
        self.subPackage = False

        # 打包信息
        # 组件源有哪些，逗号隔开。若果有不同的APP，可以用组件池区分开。基础组件，A端，B端或者C端等等。
        self.moduleSources = ""
        # 依赖的json串，
        self.dependencyJSON = ""
        # 打包的时候是否用SSH 下载，有时候提交太大，需要用SSH
        self.useSSH = False
        # 打包前是否检查
        self.check = False
        # 如果是subspec打包，则指定拿几个subspec打包，不指定则全部打
        self.subspecs = ""
        # 要不要打framework静态库
        self.framework = False
        # 要不要打debug包
        self.debugPackage = False
        # 要不要打 Release包
        self.releasePackage = False
        # 真机架构
        self.archs = ""
        # 模拟器架构
        self.archs_sim = ""



        # 打包输出结果的文件路径，会输出JSON格式的输出
        self.resultPath = ""
        # 打包后源码和静态库存放的路径，如果不提供，则在工程目录下输出二进制结果
        self.CAFPath = ""

        # 是否自动吧提交信息push到远程
        self.autoPush = False

        # 发布组件
        # 是否自动发布repo
        self.autoPushRepo = False
        # 如果自动发布repo，要发布到哪里。多个用逗号隔开
        self.repoSources = ""
        # 是否提供大文件存储的URL，如果提供，则会在发布repo的时候改变podspec 里s.source 里的URL
        self.LFSURL = ""

        self.isflutter = False
        self.flaver = ""


    def _arguments(self):
        """
        获得参数
        :param type: 哪个命令的参数
        :return:
        """
        if type == "":
            return
        try:
            opts, args = getopt.getopt(sys.argv[2:], "",
                                       ["help", "user=", "projectPath=", "subPackage=", "podName=", "branch=",
                                        "version=", "commitId=", "debug=", "dependencyJSON=", "framework", "archive",
                                        "check", "debugPackage", "releasePackage", "autoPush", "autoPushRepo",
                                        "repoSources=", "resultPath=", "whiteListPath=", "subspecs=", "CAFPath=",
                                        "LFSURL=","moduleSources=", "updateMasterSource", "useSSH", "archs=", "archs_sim=",
                                        "isFlutter=", "flaver="])
            # sys.argv[1:] 过滤掉第一个参数(它是脚本名称，不是参数的一部分)
        except getopt.GetoptError:
            self.formatter.format_error("argv error,please input")
            self.result.returnError()
        if not args and not opts:
            self.tips.showTips()
            self.result.returnError()
        # 使用一个循环，每次从opts中取出一个两元组，赋给两个变量。cmd保存选项参数，arg为附加参数。接着对取出的选项参数进行处理。
        for cmd, arg in opts:
            self.formatter.format_print(cmd + "  " + arg)
            if cmd == "--debug":
                self.debug = boolValue(arg)
            elif cmd == "--whiteListPath":
                self.whiteListPath = str(arg)
            elif cmd in ("--user"):
                self.user = str(arg)
            elif cmd in ("--projectPath"):
                self.projectPath = str(arg)
                self.projectName = self.projectPath.rstrip("/").split('/')[-1]
                self.projectParentDict = self.projectPath.replace(self.projectName, "")
            elif cmd == "--podName":
                self.podName = str(arg)
            elif cmd == "--branch":
                self.branch = str(arg)
            elif cmd in ("--version"):
                self.version = str(arg)
            elif cmd == "--commitId":
                self.commitId = str(arg)
            elif cmd == "--subPackage":
                self.subPackage = boolValue(arg)
            elif cmd == "--moduleSources":
                self.moduleSources = str(arg)
                if self.moduleSources:
                    self.moduleSourceList = self.moduleSources.strip(" ").split(",")
                else:
                    self.moduleSources = ""
                    self.moduleSourceList = []
            elif cmd == "--useSSH":
                self.useSSH = boolValue(arg)
            elif cmd == "--dependencyJSON":
                self.dependencyJSON = str(arg)
                if self.dependencyJSON:
                    self.dependencyDict = self.getDependencyDict()
                else:
                    self.dependencyDict = {}
            elif cmd == "--check":
                self.chdependeeck = boolValue(arg)
            elif cmd == "--subspecs":
                self.subspecs = str(arg)
            elif cmd == "--framework":
                self.framework = boolValue(arg)
            elif cmd == "--archive":
                self.archive = boolValue(arg)
            elif cmd == "--debugPackage":
                self.debugPackage = boolValue(arg)
            elif cmd == "--releasePackage":
                self.releasePackage = boolValue(arg)
            elif cmd == "--resultPath":
                self.resultPath = str(arg)
            elif cmd == "--CAFPath":
                self.CAFPath = str(arg)
            elif cmd == "--autoPush":
                self.autoPush = boolValue(arg)
            elif cmd == "--autoPushRepo":
                self.autoPushRepo = boolValue(arg)
            elif cmd == "--repoSources":
                self.repoSources = str(arg)
                if self.repoSources:
                    self.repoSourceList = self.repoSources.strip(" ").split(",")
                else:
                    self.repoSourceList = []
            elif cmd == "--LFSURL":
                self.LFSURL = str(arg)
            elif cmd == "--archs":
                self.archs = str(arg)
            elif cmd == "--archs_sim":
                self.archs_sim = str(arg)
            elif cmd == "--archs_sim":
                self.archs_sim = str(arg)
            elif cmd == "--isFlutter":
                self.isflutter = str(arg)
            elif cmd == "--flaver":
                self.flaver = str(arg)
            else:
                self.tips.showTips()
                self.result.returnError()

    def _checkArgues(self):
        if not self.podName and self.projectPath:
            self.podName = self.projectName
        if self.version and self.framework and (self.debugPackage or self.releasePackage):
            if len(self.version.split(".")) > 4 and len(self.version.split(".")) < 3:
                self.result.returnError(self.version + "  输入的版本号不符合规范")
            if self.projectPath:
                if os.path.isdir(self.projectPath):
                    os.chdir(self.projectPath)
                else:
                    self.result.returnError("找不到这个目录"+self.projectPath)
            returnCode, content = self.shell.excommand_until_done("git tag")
            if returnCode > 0:
                self.result.returnError("获得tag失败")
            if content:
                tagList = content.split("\n")
                tagString = self.podName + "-" + str(self.version)
                for tag in tagList:
                    if tagString == tag:
                        self.result.returnError("发现有相同的tag号, 请检查:" + tag)
            if len(self.archs) == 0 or len(self.archs_sim) == 0:
                self.result.returnError("archs 或者archs_sim 必须要都有架构")


    def getDependencyDict(self):
        if self.fileHandle.file_exist(self.dependencyJSON):
            # 文件形式
            self.dependencyJSON = self.fileHandle.readFile(self.dependencyJSON)
        dependencyDict = json.loads(self.dependencyJSON)
        return byteify(dependencyDict)

    def argumentDict(self):
        return {
            "user": self.user,"projectPath": self.projectPath,"podName": self.podName,
            "branch":self.branch,"version": self.version,"commitId":self.commitId,
            "subPackage":self.subPackage,"moduleSources":self.moduleSources,
            "dependencyJSON": self.dependencyJSON,"useSSH":self.useSSH,"check":self.check,
            "subspecs": self.subspecs, "framework":self.framework, "debugPackage":self.debugPackage,
            "releasePackage":self.releasePackage, "resultPath":self.resultPath, "CAFPath": self.CAFPath,
            "autoPush": self.autoPush, "autoPushRepo": self.autoPushRepo, "repoSources":self.repoSources,
            "LFSURL":self.LFSURL,
        }


