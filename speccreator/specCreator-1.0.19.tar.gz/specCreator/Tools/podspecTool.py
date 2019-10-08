#!/usr/bin/env python
# -*- coding=utf-8 -*-


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

class PodspecTool(object):

    __instance = None

    def __init__(self):
        self.formatter = Formatter.instance()
        self.arguments = Arguments.instance()
        self.fileHandle = FileHandle.instance()
        self.result = Result.instance()
        self.shell = Shell.instance()
        self.urlTool = URL.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = PodspecTool()
        return cls.__instance

    def supportBinary(self):
        # changeSpec(podName, subPackage)
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
            self.formatter.format_print("即将替换" + sourceKey)
            if subPackage:
                replaceContent = replaceContent.replace(sourceKey, packageBySubspec, 1)
            else:
                replaceContent = replaceContent.replace(sourceKey, noSubSpec, 1)
        else:
            self.result.returnError("错误，没有找到关键字source_files ，可能已经完成替换或者其他的未知错误")
        self.fileHandle.writeToFile(replaceContent, originSpecPath)

    # TODO 不好。
    def changePodSpec(self, podName, subspecName="", version="", useTag=True, commitId="", dependencyDict={}, LFSURL="", replaceName=True, useSSH=False):
        podspecName = podName + subspecName
        originSpecPath = podName + ".podspec"
        if not self.fileHandle.file_exist(originSpecPath):
            self.result.returnError(originSpecPath + "文件不存在，请检查工程名或者podName是否正确")
        # content = self.fileHandle.readFile(originSpecPath)
        contentList = []
        for lineStr in self.fileHandle.readLines(originSpecPath):
            tmpLineStr = lineStr.replace("\t", "").strip(" ")
            if str(tmpLineStr).startswith("#"):
                contentList.append(lineStr)
                continue
            tmpLineStr = tmpLineStr.replace("\n", "")
            if str(tmpLineStr).startswith("s.name") and tmpLineStr.find(podName) > -1:
                originLine = tmpLineStr
                replaceSpecName = tmpLineStr.replace(podName, podspecName, 1)
                self.formatter.format_info("把" + lineStr + "替换成" + replaceSpecName)
                lineStr = lineStr.replace(originLine, replaceSpecName)
            elif str(tmpLineStr).startswith("s.version"):
                originLine = tmpLineStr
                if version:
                    replaceVersion = "s.version          = \'" + version + "\'"
                    self.formatter.format_info("把" + lineStr + "替换成" + replaceVersion)
                    lineStr = lineStr.replace(originLine, replaceVersion)
            elif tmpLineStr.startswith("s.source") and tmpLineStr.find(":git") > -1:
                originSourceLine = tmpLineStr
                replaceSource = tmpLineStr
                if useSSH:
                    urlList = self.urlTool.getUrl(tmpLineStr)
                    if urlList and len(urlList) > 0:
                        url = urlList[0]
                        urlProtol, s1 = self.urlTool.URLProtocol(url)
                        host, port = self.urlTool.URLHostAndPort(url)
                        replaceSource = replaceSource.replace(urlProtol, "ssh").replace(host, self.arguments.user + "@" + host + ":29418")
                replaceSource = str(replaceSource).strip("\n").strip("").split(",")[0].strip("}")
                if LFSURL:
                    # if not self.urlTool.isURL(LFSURL):
                    #     self.result.returnError("提供的LFSURL不是格式不规范，请检查：" + LFSURL)
                    # 如果存在远程大文件存储服务器，pushrepo的时候，需要改成服务器下载地址
                    replaceSource = "s.source = { :http => \"" + LFSURL + "\""
                if commitId:
                    commitId = commitId.strip("\n")
                    if tmpLineStr.find(":commit") > -1 or tmpLineStr.find(":tag"):
                        replaceSource += ", :commit => \"" + commitId + "\" }"
                elif useTag:
                    replaceSource += ", :tag => s.name.to_s + \"-\" + s.version.to_s }"
                else:
                    replaceSource += " }"

                if replaceSource:
                    self.formatter.format_info("把" + tmpLineStr + "替换成" + replaceSource)
                    lineStr = lineStr.replace(originSourceLine, replaceSource)
            elif tmpLineStr.find(":dependency =>") > -1:
                originLine = tmpLineStr
                propertyLine = str(tmpLineStr).split(":dependency =>")[-1].replace("[", "").replace("{", ""). \
                    replace("}", "").replace("]", "")
                nameList = matchList(r":name +=> +\"(\w+?)\"", propertyLine)
                if nameList and nameList[0] in dependencyDict.keys():
                    specName = nameList[0]
                    versionList = matchList(r":version +=> +\"(.+?)\"", propertyLine)
                    if len(versionList) == 1:
                        if not isinstance(dependencyDict[specName], list):
                            self.result.returnError("给的字典值必须是数组")
                        replaceLine = dependencyDict[specName][-1]
                        self.formatter.format_info("把依赖：" + versionList[0] + "\n变成：   " + replaceLine + "\n")
                        lineStr = lineStr.replace(versionList[0], replaceLine)
            elif tmpLineStr.find("#{s.name}") > -1 and replaceName:
                originLine = tmpLineStr
                replaceLine = tmpLineStr.replace("#{s.name}", podName)
                self.formatter.format_info("把库名：" + tmpLineStr + "\n变成：   " + replaceLine + "\n")
                lineStr = lineStr.replace(originLine, replaceLine)
            elif tmpLineStr.find(".dependency ") > -1:
                originLine = tmpLineStr
                specName = tmpLineStr.split(" ")[-1].strip("\"").strip("\'").split("/")[0]
                if specName in dependencyDict.keys() and str.isalnum(specName[0]):
                    if not isinstance(dependencyDict[specName], list):
                        self.result.returnError("给的字典值必须是数组")
                    versionString = ""
                    for version in dependencyDict[specName]:
                        versionString += ", \"" + version + "\""
                    replaceLine = tmpLineStr + versionString
                    self.formatter.format_info("把" + lineStr + "替换成" + replaceLine)
                    lineStr = lineStr.replace(originLine, replaceLine)
            contentList.append(lineStr)
        # 去掉最后一个end
        endString = ""
        while (endString != "end"):
            endString = contentList.pop().strip("\n").strip("")
            print endString
        for key, versionList in dependencyDict.items():
            versionString = ""
            for vString in versionList:
                versionString += "\"" + vString + "\", "
            versionString = versionString.strip(" ").rstrip(",")
            dependencyString = "  s.dependency  \"" + str(key) + "\""
            if versionString:
                dependencyString += ", " + versionString
            contentList.append(dependencyString + "\n")
            self.formatter.format_info("添加依赖：" + dependencyString)
        contentList.append("end")
        replaceContent = "".join(contentList)
        self.fileHandle.writeToFile(replaceContent, podspecName + ".podspec")

    def changePodSpecForTmpPodspec(self, subSpecName):
        podName = self.arguments.podName
        dependencyDict = self.arguments.dependencyDict
        commitID = self.arguments.commitId
        version = self.arguments.version.split("-")[0]
        self.changePodSpec(podName + subSpecName, "Tmp", version, False, commitID, dependencyDict, "" , True, False)


    def changePodSpecForCheck(self):
        podName = self.arguments.podName
        dependencyDict = self.arguments.dependencyDict
        commitID = self.arguments.commitId
        version = self.arguments.version
        self.changePodSpec(podName, "", version ,False, commitID, dependencyDict)

    def changePodSpecForPackage(self, subspecName):
        podName = self.arguments.podName
        dependencyDict = self.arguments.dependencyDict
        commitId = self.arguments.commitId
        version = self.arguments.version
        self.changePodSpec(podName, subspecName, version,False, commitId, dependencyDict, "", True, self.arguments.useSSH)

    def changePodspecForPush(self):
        podName = self.arguments.podName
        version = self.arguments.version
        self.changePodSpec(podName, "", version, True, "", {}, "", False)

    def changePodspecForPushRepo(self):
        podName = self.arguments.podName
        LFSURL = self.arguments.LFSURL
        useTag = True
        if len(LFSURL):
            useTag = False
        version = self.arguments.version
        self.changePodSpec(podName, "", version, useTag, "", {}, LFSURL, False)



    def subspecList(self):
        """
        获得subspec的列表
        :param podName: pod库名称
        :return:
        """
        podName = self.arguments.podName
        podspecDict = self.getSpecDict(podName)
        subspecNameList = []
        if "subspecs" not in podspecDict.keys():
            self.result.returnError("没有subspec要打包，如果不需要每个subspec单独打包，请把subPackage设置成false")
        if podspecDict["subspecs"]:
            for subspec in podspecDict["subspecs"]:
                subspecNameList.append(subspec["name"])
        return byteify(subspecNameList)

    def getSpecDict(self, podName):
        returnCode, content = self.shell.excommand_until_done("IS_SOURCE=1 pod ipc spec " + podName + ".podspec")
        contentList = matchList("({.+}$)", content)
        if returnCode > 0 or not contentList:
            self.result.returnError("podspec 有问题，不能转换成JSON数据")
        specJson = contentList[0]
        specDict = json.loads(specJson)
        return byteify(specDict)

    def canPackage(self, podName, subspecName):
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

    def redirectSubSpec(self, originSpecPath):
        self.formatter.format_info(" 正在重定向subspec的dependency，为打包做准备")
        if not self.fileHandle.file_exist(originSpecPath):
            self.result.returnError(originSpecPath + "需要重定向的文件不存在，请检查工程名或者podName是否正确")
        content = self.fileHandle.readFile(originSpecPath)
        contentList = []
        for lineStr in self.fileHandle.readLines(originSpecPath):
            tmpLineStr = lineStr.strip(" ")
            if str(tmpLineStr).startswith("#"):
                contentList.append(lineStr)
                continue
            tmpLineStr = tmpLineStr.replace("\n", "")
            if tmpLineStr.startswith("ss.dependency ") > -1 and tmpLineStr.find("/#{dep[:spec_name]}") > -1:
                originLine = tmpLineStr
                replaceLine = "ss.dependency \"#{s.name}Tmp/#{dep[:spec_name]}\""
                self.formatter.format_info("把" + lineStr + "替换成" + replaceLine)
                lineStr = lineStr.replace(originLine, replaceLine)
            contentList.append(lineStr)
        replaceContent = "".join(contentList)
        # 把原podspec重命名
        self.fileHandle.writeToFile(replaceContent, originSpecPath)

    def backUpPodspec(self):
        originSpecName = self.arguments.podName + ".podspec"
        destinationSpecName = originSpecName + ".old"
        if self.fileHandle.file_exist(originSpecName) and not self.fileHandle.file_exist(destinationSpecName):
            self.shell.excommand_until_done("cp -rf " + originSpecName + " " + destinationSpecName)

    def restorePodspec(self):
        destinationSpecName = self.arguments.podName + ".podspec"
        originSpecName = destinationSpecName + ".old"
        if self.fileHandle.file_exist(originSpecName):
            self.shell.excommand_until_done("cp -rf " + originSpecName + " " + destinationSpecName)
        self.deleteBackUpPodspec()

    def deleteBackUpPodspec(self):
        BackUpPodspec = self.arguments.podName + ".podspec" + ".old"
        if self.fileHandle.file_exist(BackUpPodspec):
            self.shell.excommand_until_done("rm " + BackUpPodspec)