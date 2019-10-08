#!/usr/bin/env python
# -*- coding=utf-8 -*-


import sys
import os
import importlib
import yaml
import json
from constant import *
from arguments import Arguments
from formatter import Formatter
from result import Result
from commonFuncs import *
from tips import Tips
from fileHandle import FileHandle
from shellCommand import Shell
from url import URL
from gitTool import GitTool
from podspecTool import PodspecTool


class CocoapodsTool(object):

    __instance = None

    def __init__(self):
        self.formatter = Formatter.instance()
        self.result = Result.instance()
        self.tips = Tips.instance()
        self.fileHandle = FileHandle.instance()
        self.shell = Shell.instance()
        self.arguments = Arguments.instance()
        self.URL = URL.instance()
        self.gitTool = GitTool.instance()
        self.podspecTool = PodspecTool.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = CocoapodsTool()
        return cls.__instance

    def libCreate(self):
        """
        初始化spec模板并交互
        """
        self.formatter.format_info("正在初始化工程模板...")
        user = self.arguments.user
        projectName = self.arguments.projectName
        cmd = "pod lib create " + projectName
        pexpect = importlib.import_module('pexpect')
        pexpect.logfile = sys.stdout
        q0 = "What is your name?"
        q1 = "What is your email?"
        q2 = "What platform do you want to use"
        q3 = "What language do you want to use?"
        q4 = "Would you like to include a demo application with your library?"
        q5 = "Which testing frameworks will you use?"
        q6 = "Would you like to do view based testing?"
        q7 = "What is your class prefix?"
        email = user + emailSuffix
        child = pexpect.spawn(cmd)
        isRuning = True
        while isRuning:
            index = child.expect([q0, q1, q2, q3, q4, q5, q6, q7, pexpect.EOF, pexpect.TIMEOUT])
            if index == 0:
                self.formatter.format_print(q0)
                self.formatter.format_print(user)
                child.sendline(user)
            elif index == 1:
                self.formatter.format_print(q1)
                self.formatter.format_print(email)
                child.sendline(email)
            elif index == 2:
                self.formatter.format_print(q2)
                self.formatter.format_print(platform)
                child.sendline(platform)
            elif index == 3:
                self.formatter.format_print(q3)
                self.formatter.format_print(language)
                child.sendline(language)
            elif index == 4:
                self.formatter.format_print(q4)
                self.formatter.format_print(demo)
                child.sendline(demo)
            elif index == 5:
                self.formatter.format_print(q5)
                self.formatter.format_print(testing)
                child.sendline(testing)
            elif index == 6:
                self.formatter.format_print(q6)
                self.formatter.format_print(based)
                child.sendline(based)
            elif index == 7:
                self.formatter.format_print(q7)
                self.formatter.format_print(prefix)
                child.sendline(prefix)
            elif index == 8:
                self.formatter.format_print("初始化模板成功")
                isRuning = False
            elif index == 9:
                isRuning = False
                self.result.returnError("模板初始化超时")
            else:
                self.result.returnError("脚本出错，请检查")
        return not isRuning

    def repoDict(self):
        returnCode, content = self.shell.excommand_until_done("pod repo list")
        if returnCode > 0:
            self.result.returnError("pod repo list 失败")
        # content = matchList("lianjia-mobile_.*", content)[0]
        contentLines = content.split("\n")
        yamlContent = ""
        for line in contentLines:
            if not line or " repo" in line:
                continue
            if ":" not in line:
                line += " :"
            if str(line).startswith("-"):
                line = line.replace("-", " ", 1)
            yamlContent += line + "\n"
        repoDict = yaml.load(yamlContent)
        return repoDict

    def updateRepoList(self, repoList):
        for repoUrl in repoList:
            repoName = self.repoNameFromURL(repoUrl)
            self.updateRepo(repoName)

    def updateRepo(self, repoName):
        self.shell.excommand_until_done("pod repo update " + repoName)

    def addRepo(self, repoURL):
        repoName = self.repoNameFromURL(repoURL)
        userPath = os.path.expanduser('~')
        repoPath = userPath + "/.cocoapods/repos/" + repoName
        if not self.fileHandle.file_exist(repoPath):
            self.shell.excommand_until_done(
                "pod repo add " + repoName + " " + repoURL)

    def cleanRepo(self, repoName):
        userPath = os.path.expanduser('~')
        repoPath = userPath + "/.cocoapods/repos/" + repoName
        if not self.fileHandle.file_exist(repoPath):
            self.result.returnError("要清除的repo不存在")
        else:
            self.gitTool.clean(repoPath)
            self.updateRepo(repoName)

    def pushRepo(self, podName, version, repoUrl):
        # 获取用户目录
        repoPath = self.repoPathByURL(repoUrl)
        if not self.fileHandle.file_exist(repoPath):
            self.addRepo(repoUrl)
        repoName = self.repoNameFromURL(repoUrl)
        self.cleanRepo(repoName)
        self.copyPodspecToRepo(podName, version, repoPath)
        commitMsg = "自动发布" + podName + "的版本：" + version
        self.gitTool.commit(commitMsg, repoPath)
        returnCode, content = self.gitTool.push(repoPath)
        if returnCode > 0:
            self.result.returnError("发布repo失败。请检查发布repo的权限。")

    def copyPodspecToRepo(self, podName, version, repoPath):
        podspecFileName = podName + ".podspec"
        podspecPath = repoPath + "/" + podName + "/" + version
        if self.fileHandle.file_exist(podspecPath):
            self.formatter.format_error("可能存在相同tag的的podspec，请检查" + podspecPath)
        returnCode, content = self.shell.excommand_until_done("mkdir -p " + podspecPath)
        if returnCode > 0:
            self.result.returnError("创建文件夹失败")
        returnCode, content = self.shell.excommand_until_done(
            "cp ./" + podspecFileName + " " + podspecPath + "/" + podspecFileName)
        if returnCode > 0:
            self.result.returnError("移动临时podspec失败")


    def repoPathByURL(self, repoURL):
        repoName = self.repoNameFromURL(repoURL)
        userPath = os.path.expanduser('~')
        repoPath = userPath + "/.cocoapods/repos/" + repoName
        return repoPath

    def repoNameFromURL(self, repoURL):
        if not self.URL.isURL(repoURL):
            self.result.returnError("url 不合法")
        repoURL = repoURL.strip(".git")
        host, port = self.URL.URLHostAndPort(repoURL)
        hostList = str(host).split(".")
        hostName = ""
        if len(hostList) == 3:
            hostName = hostList[1]
        tmp, path = self.URL.URLPath(repoURL)
        path = str(path).replace("/", "-")
        return hostName + path

    def cleanRepoEnv(self, repoList=[]):
        if len(repoList) == 0:
            repoDict = self.repoDict()
            repoList = repoDict.keys()
        for repoName in repoList:
            self.cleanRepo(repoName)

    def libLint(self):
        podName = self.arguments.podName
        podspecName = podName + ".podspec"
        self.formatter.format_info("正在检测" + podspecName + "是否配置正确（前提是远程已经有写好的Spec文件）。")
        self.podspecTool.backUpPodspec()
        self.podspecTool.changePodSpecForCheck()
        # 太耗时，能用二进制的用二进制
        cmd = "IS_SOURCE=1 pod lib lint " + podspecName + " --allow-warnings --verbose --use-libraries --sources="
        cmd += self.arguments.moduleSources + "  --fail-fast --no-clean"
        returnCode, message = self.shell.excommand_until_done(cmd)
        if returnCode > 0:
            self.result.returnError("podspec 检测不通过，请检查podspec或者提供的dependencyJSON是否有问题。")
        self.podspecTool.restorePodspec()

    def create_tmp_podspec(self, subSpecName):
        commitId = self.arguments.commitId
        podName = self.arguments.podName
        version = self.arguments.version.split("-")[0]
        dependencyDict = self.arguments.dependencyDict
        if not commitId:
            self.result.returnError("subspec 打包必须要commitId")
        self.podspecTool.changePodSpecForTmpPodspec(subSpecName)
        userPath = os.path.expanduser('~')
        # repoSourceList = self.arguments.repoSourceList
        repoSource = self.arguments.moduleSourceList[0]
        repoName = self.repoNameFromURL(repoSource)
        repoPath = userPath + "/.cocoapods/repos/" + repoName
        if not self.fileHandle.file_exist(repoPath):
            returnCode, content = self.shell.excommand_until_done("pod repo add " + repoName + " " + repoSource)
            if returnCode > 0:
                self.result.returnError(repoSource + "添加repo失败，请确认是否再内网。")
        else:
            self.cleanRepo(repoName)
        tmpPodspecFileName = podName + subSpecName + "Tmp.podspec"
        tmpPodspecPath = repoPath + "/" + podName + subSpecName + "Tmp/" + version
        if self.fileHandle.file_exist(tmpPodspecPath):
            self.formatter.format_warning("可能存在已经有的podspec，请检查" + tmpPodspecPath)
        returnCode, content = self.shell.excommand_until_done("mkdir -p " + tmpPodspecPath)
        if returnCode > 0:
            self.result.returnError("创建文件夹失败")
        returnCode, content = self.shell.excommand_until_done(
            "mv ./" + tmpPodspecFileName + " " + tmpPodspecPath + "/" + tmpPodspecFileName)
        if returnCode > 0:
            self.result.returnError("移动临时podspec失败")



