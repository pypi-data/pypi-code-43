#!/usr/bin/env python
# -*- coding=utf-8 -*-


import sys
import os
import glob
import json
import shutil
from Tools.tips import Tips
from Tools.result import Result
from Tools.formatter import Formatter
from Tools.fileHandle import FileHandle
from Tools.shellCommand import Shell
from Tools.arguments import Arguments
from Tools.gitTool import GitTool
from Tools.cocoapodsTool import CocoapodsTool
from Tools.podspecTool import PodspecTool
from package import Package
from check import Check
from Tools.resultModel import ResultModel


class AutoPackage(object):
    __instance = None

    def __init__(self):
        self.formatter = Formatter.instance()
        self.result = Result.instance()
        self.tips = Tips.instance()
        self.fileHandle = FileHandle.instance()
        self.shell = Shell.instance()
        self.arguments = Arguments.instance()
        self.gitTool = GitTool.instance()
        self.cocoapodsTool = CocoapodsTool.instance()
        self.podspecTool = PodspecTool.instance()
        self.package = Package.instance()
        self.resultModel = ResultModel.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = AutoPackage()
        return cls.__instance

    def cpCodeAndSourcesToCAFPath(self):
        CAFPath = self.arguments.CAFPath
        projectPath = self.arguments.projectPath
        podName = self.arguments.podName
        if not self.fileHandle.file_exist(CAFPath):
            self.shell.excommand_until_done("mkdir -p " + CAFPath)
        # 找到源码和资源位置。因为有些库不规范，只能从podspec下手
        specDict = self.podspecTool.getSpecDict(podName)
        if "preserve_paths" not in specDict.keys():
            self.result.returnError("podspec 不符合规范，必须要有preserve_paths 字段")
        preserve_paths = specDict["preserve_paths"]
        if isinstance(preserve_paths, str):
            preserve_paths = [preserve_paths]
        for path in preserve_paths:
            if str(path).startswith(podName + "/Framework/") or str(path).startswith(podName + "/Archive/"):
                continue
            fileList = self.myGlob(path)
            for filePath in fileList:
                relativePath = str(filePath).replace(projectPath, "").rstrip("/")
                # 拼接目标文件或者文件加的绝对路径
                abstargetPath = os.path.join(CAFPath, relativePath)
                # 是文件就进行复制
                if os.path.isdir(filePath):
                    if not self.fileHandle.file_exist(abstargetPath):
                        self.shell.excommand_until_done("mkdir -p " + abstargetPath)
                elif os.path.isfile(filePath):
                    targetDic = os.path.dirname(abstargetPath)
                    if not self.fileHandle.file_exist(targetDic):
                        self.shell.excommand_until_done("mkdir -p \"" + targetDic + "\"")
                    self.shell.excommand_until_done("cp -R -p \"" + filePath + "\" \"" + abstargetPath + "\"")

    def autoPackage(self):
        projectPath = self.arguments.projectPath
        os.chdir(projectPath)
        podName = self.arguments.podName
        version = self.arguments.version
        commitId = self.arguments.commitId
        branch = self.arguments.branch
        self.resultModel.recordResultDict()
        self.resultModel.recordVersionHistory()
        self.formatter.format_info("正在清理现场")
        self.gitTool.clean()
        self.formatter.format_info("正在拉取远程代码")
        self.gitTool.pull()
        # 判断branch和commit
        self.formatter.format_info("正在切换到分支" + branch)
        self.gitTool.checkout(branch)
        self.arguments.branch, self.arguments.commitId = self.gitTool.currentBranchAndCommitID()
        # 清理过期的库
        self.cleanDeprecatedStaticLibraries()
        if self.arguments.check:
            self.formatter.format_info("执行打包前检测")
            Check.instance().libLint()

        self.formatter.format_info("正在处理静态库目标文件")
        CAFPath = self.arguments.CAFPath
        if CAFPath:
            self.cpCodeAndSourcesToCAFPath()

        # 开始打静态库。
        self.package.package()
        self.resultModel.saveVersionHistory()
        if self.arguments.autoPush:
            self.formatter.format_info("正在自动提交")
            commitMessage = "自动打静态库:" + podName + " " + version
            returnCode, content = self.shell.excommand_until_done("git status")
            if "nothing to commit, working tree clean" not in content:
                self.gitTool.commit(commitMessage)
            # returnCode, newCommitId = self.shell.excommand_until_done("git rev-parse " + branch)
            self.podspecTool.changePodspecForPush()
            returnCode, content = self.shell.excommand_until_done("git status")
            if "nothing to commit, working tree clean" not in content:
                self.shell.excommand_until_done("git add . ")
                self.shell.excommand_until_done("git commit -m \'发布" + podName + "-" + version + "\'")
            returnCode, content = self.shell.excommand_until_done("git push origin")
            if returnCode > 0:
                self.result.returnError("git push 失败，请确认你是否有权限")
            ResultModel.instance().resultDict["autoPushSuccess"] = True
        if self.arguments.autoPushRepo:
            if not self.arguments.repoSources:
                self.result.returnError("自动发布请指定发布源参数：--repoSources")
            self.formatter.format_info("正在自动发布")
            tagVersion = podName + "-" + version
            self.shell.excommand_until_done("git tag " + tagVersion)
            returnCode, content = self.shell.excommand_until_done("git push origin " + tagVersion)
            if returnCode > 0:
                self.result.returnError("tag push 失败"+ content)
            self.podspecTool.changePodspecForPushRepo()
            # 最好先清空下repo，防止repo污染
            repoSourceList = self.arguments.repoSourceList
            for repoSource in repoSourceList:
                self.formatter.format_info("正在发布到：" + repoSource)
                self.cocoapodsTool.pushRepo(podName, version, repoSource)
            ResultModel.instance().resultDict["autoPushRepoSuccess"] = True
        # 保存结果信息
        self.resultModel.saveResultPath()
        if self.arguments.releasePackage:
            self.resultModel.uploadPodInfo()
        self.formatter.format_info("二进制打包成功")

    def canPackage(self, subspecName=""):
        podName = self.arguments.podName
        specDict = self.getSpecDict(podName)
        sourcePathList = []
        if not subspecName:
            if "source_files" in specDict.keys():
                sourcePath = specDict["source_files"]
                if isinstance(sourcePath, str):
                    sourcePath = [sourcePath]
                sourcePathList.extend(sourcePath)
            if "subspecs" in specDict.keys():
                subspecs = specDict["subspecs"]
                for subspec in subspecs:
                    if "source_files" in subspec.keys():
                        sourcePath = subspec["source_files"]
                        if isinstance(sourcePath, str):
                            sourcePath = [sourcePath]
                        sourcePathList.extend(sourcePath)
        else:
            if "subspecs" in specDict.keys():
                subspecs = specDict["subspecs"]
                for subspec in subspecs:
                    if "name" in subspec.keys():
                        if subspecName != subspec["name"]:
                            continue
                    if "source_files" in subspec.keys():
                        sourcePath = subspec["source_files"]
                        if isinstance(sourcePath, str):
                            sourcePath = [sourcePath]
                        sourcePathList.extend(sourcePath)

        for sourcePath in sourcePathList:
            splitString = ""
            if "/**/*" in sourcePath:
                splitString = "/**/*"
            elif "/**/" in sourcePath:
                splitString = "/**/"
            elif "/*" in sourcePath:
                splitString = "/*"
            else:
                splitString = "/"
            tmpList = sourcePath.split(splitString)
            intersection = ["m", "mm", "c", "cpp", "cc"]
            if len(tmpList) >= 2:
                if tmpList[-1] != "":
                    suffixList = tmpList[-1].strip("{").strip("}").replace(".", "").split(",")
                    usefulSuffixList = ["m", "mm", "c", "cpp", "cc"]
                    intersection = [val for val in suffixList if val in usefulSuffixList]
                    if not intersection:
                        continue
                    sourcePath = sourcePath.rstrip(tmpList[-1])
            sourcePath = sourcePath.rstrip(splitString)
            for suffix in intersection:
                files = self.findfiles(sourcePath, "." + suffix, True)
                if not files:
                    continue
                return True
        return False

    def findfiles(self, dirname, suffix, recursion=False):
        result = []
        for fileName in os.listdir(dirname):
            filePath = os.path.join(dirname, fileName)
            if os.path.isfile(filePath):
                if filePath.endswith(suffix):
                    result.append(filePath)
            elif recursion and os.path.isdir(filePath):
                result.extend(self.findfiles(filePath, suffix, recursion))
        return result

    def cleanDeprecatedStaticLibraries(self):
        self.formatter.format_info("正在清理陈旧的库")
        frameWorkPath = os.path.join(self.arguments.podName, "Framework")
        if self.arguments.framework and (self.arguments.debugPackage or self.arguments.releasePackage):
            if self.arguments.subPackage:
                if self.arguments.subspecs:
                    for subspec in self.arguments.subspecs:
                        self.shell.excommand_until_done("rm -r -f " + frameWorkPath + "/" + subspec)
                else:
                    self.shell.excommand_until_done("rm -r -f " + frameWorkPath)
            else:
                self.shell.excommand_until_done("rm -r -f " + frameWorkPath)


    def myGlob(self, path, recursion=False):
        # 绝对路径查找
        # TODO 有问题，当写上后缀的时候。
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        if "/**/" in path:
            recursion = True
            dirname = path.split("/**/")[0]
            basename = path.split("/**/")[1]
        if not self.fileHandle.file_exist(dirname):
            return []
        fileList = glob.glob(os.path.join(dirname, basename))
        if recursion:
            for fileName in os.listdir(dirname):
                fileDir = os.path.join(dirname, fileName)
                nestBasename = os.path.join(fileDir, basename)
                if os.path.isdir(fileDir):
                    nextFileList = self.myGlob(nestBasename, recursion)
                    if nextFileList:
                        fileList.extend(nextFileList)
        return list(set(fileList))
