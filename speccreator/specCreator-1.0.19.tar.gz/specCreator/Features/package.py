#!/usr/bin/env python
# -*- coding=utf-8 -*-

import os
import sys
import importlib
import glob
from Tools.tips import Tips
from Tools.result import Result
from Tools.formatter import Formatter
from Tools.fileHandle import FileHandle
from Tools.shellCommand import Shell
from Tools.arguments import Arguments
from Tools.cocoapodsTool import CocoapodsTool
from Tools.podspecTool import PodspecTool
from Tools.resultModel import ResultModel
from Tools.commonFuncs import *


class Package(object):
    __instance = None

    def __init__(self):
        self.formatter = Formatter.instance()
        self.result = Result.instance()
        self.tips = Tips.instance()
        self.fileHandle = FileHandle.instance()
        self.shell = Shell.instance()
        self.arguments = Arguments.instance()
        self.cocoaPodsTool = CocoapodsTool.instance()
        self.podspecTool = PodspecTool.instance()


    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = Package()
        return cls.__instance

    def package(self):
        if not self.arguments.framework:
            return
        frameworkPath = os.path.join(self.arguments.podName, "/Framework")
        if self.arguments.debugPackage:
            self.formatter.format_info("正在打 framework debug 二进制库")
            self.packageFramework(True)
            ResultModel.instance().resultDict["debugFrameworkPath"] = os.path.join(frameworkPath, "Debug")
        if self.arguments.releasePackage:
            self.formatter.format_info("正在打 framework Release 二进制库")
            self.packageFramework(False)
            ResultModel.instance().resultDict["debugFrameworkPath"] = os.path.join(frameworkPath, "Release")



    def packageFramework(self, debug):
        os.chdir(self.arguments.projectPath)
        subPackage = self.arguments.subPackage
        podName = self.arguments.podName
        contentDict = {}
        if subPackage:
            subspecNames = []
            subspecs = self.arguments.subspecs
            if len(subspecs) == 0:
                subspecNames = self.podspecTool.subspecList()
            else:
                subspecNames = subspecs
            ResultModel.instance().resultDict["subspecs"] =subspecNames
            for subspec in subspecNames:
                content = self.startPackage(subspec, debug)
                contentDict[subspec] = content
        else:
            if self.arguments.isflutter:
                content = self.flutterPackage("", debug)
            else:
                content = self.startPackage("", debug)
                contentDict[podName] = content
        if contentDict:
            dependency = self.processDependency(contentDict)
            ResultModel.instance().resultDict["dependency"] = dependency
            ResultModel.instance().versionHistory += "* dependency :" + str(dependency)


    def flutterPackage(self, subSpecName, debug):
        # flutter clean
        self.shell.excommand_until_done("flutter clean")
        # self.shell.excommand_until_done("flutter packages get")

        # 找到所有的plugin
        pluginSource = "ios/pluginSource"
        pluginList = os.listdir(pluginSource)
        # 获取所有的pluggin framework

        # 清理现场
        self.shell.excommand_until_done("rm -rf build")
        self.shell.excommand_until_done("rm -rf combineDir")
        self.shell.excommand_until_done("mkdir -p combineDir/deviceApp")
        self.shell.excommand_until_done("mkdir -p combineDir/simulatorApp")

        if debug:
            flavercmd = ""
            if self.arguments.flaver:
                flavercmd = " --flavor " + self.arguments.flaver
            # 生成真机
            self.shell.excommand_until_done("flutter build ios --debug --no-simulator --no-codesign" + flavercmd)
            self.shell.excommand_until_done("cp ios/Flutter/App.framework/App combineDir/deviceApp")
            self.shell.excommand_until_done("lipo -info combineDir/deviceApp/App")
            self.copyPluginBinarys(pluginList, "build/ios/Debug-iphoneos", "combineDir/deviceApp")
            # 生成模拟器
            self.shell.excommand_until_done("flutter build ios --debug --simulator --no-codesign")
            self.shell.excommand_until_done("cp ios/Flutter/App.framework/App combineDir/simulatorApp")
            self.shell.excommand_until_done("lipo -info combineDir/simulatorApp/App")
            self.copyPluginBinarys(pluginList, "build/ios/Debug-iphonesimulator", "combineDir/simulatorApp")
            # 合并 App
            self.shell.excommand_until_done("lipo -create combineDir/simulatorApp/App combineDir/deviceApp/App -output ios/Flutter/App.framework/App")
            self.unionBinary(pluginList, "combineDir/deviceApp", "combineDir/simulatorApp", "combineDir")
        else:
            buildCMD = "flutter build ios --release  --no-codesign"
            if self.arguments.flaver:
                buildCMD += " --flavor " + self.arguments.flaver
            # 产生APP.framework
            self.shell.excommand_until_done(buildCMD)
        podName = self.arguments.podName
        productDir = os.path.join(self.arguments.projectPath, podName)
        CAFPath = self.arguments.CAFPath
        if CAFPath:
            if not self.fileHandle.file_exist(CAFPath):
                self.formatter.format_warning("存放二进制目录不存在，正在创建存放源码二进制的目录")
                self.shell.excommand_until_done("mkdir -p " + CAFPath)
            productDir = os.path.join(CAFPath, podName)
        if self.arguments.framework:
            productDir = os.path.join(productDir, "Framework")
        productPath = ""
        if debug:
            productDir += "/Debug"
        else:
            productDir += "/Release"
        # 插件生成Framework
        for plugin in pluginList:
            if plugin.startswith("."):
                continue
            # 生成framework
            binaryPath = "build/ios/Release-iphoneos/"+plugin + "/lib" + plugin + ".a"
            if debug:
                binaryPath = "combineDir/" + plugin
            self.createFramework(os.path.join(productDir, plugin+".framework"), plugin, binaryPath)
        os.chdir(self.arguments.projectPath)
        # 把APP.framework Flutter.framework 移动到指定位置。
        if self.fileHandle.file_exist("ios/Flutter/Flutter.framework"):
            returnCode, content = self.shell.excommand_until_done("cp -R -p ios/Flutter/Flutter.framework " + productDir)
            if returnCode != 0:
                self.result.returnError("复制Flutter.framework失败:"+ content)
        if self.fileHandle.file_exist("ios/Flutter/App.framework"):
            self.shell.excommand_until_done("cp -R -p ios/Flutter/App.framework " + productDir)
            if returnCode != 0:
                self.result.returnError("复制App.framework失败:"+ content)
        self.formatter.format_info("搞定")

    def copyPluginBinarys(self, pluginList, sourcePath, tagretPath):
        """
        复制插件到指定目录
        :param pluginList: 插件目录
        :param sourcePath: 原路径
        :param tagretPath: 目的路径
        """
        for plugin in pluginList:
            if plugin.startswith("."):
                continue
            sourceLibPath = sourcePath + "/" + plugin + "/lib" + plugin + ".a"
            if not self.fileHandle.file_exist(sourceLibPath):
                self.result.returnError(plugin + "没有找到")
            self.shell.excommand_until_done("cp -R -p " + sourceLibPath + " " + tagretPath)

    def unionBinary(self, pluginList, devicePath, simulatorPath, tagretPath):
        """
        合并插件的二进制
        :param pluginList: 插件列表
        :param devicePath: 真机架构二进制路径
        :param simulatorPath: 模拟器架构二进制路径
        :param tagretPath: 合并后的二进制路径
        """
        for plugin in pluginList:
            if plugin.startswith("."):
                continue
            pluginDevicePath = devicePath + "/lib" + plugin + ".a"
            pluginSimulatorPath = simulatorPath + "/lib" + plugin + ".a"
            pluginTargetPath = os.path.join(tagretPath, plugin)
            if not self.fileHandle.file_exist(pluginDevicePath):
                self.result.returnError(pluginDevicePath + "找不到真机的二进制")
            if not self.fileHandle.file_exist(pluginSimulatorPath):
                self.result.returnError(plugin + "找不到模拟器的二进制")
            returnCode, content = self.shell.excommand_until_done("lipo -create " + pluginDevicePath + " " + pluginSimulatorPath + " -output " + pluginTargetPath)
            if "error" in content:
                self.result.returnError("合并" + plugin + "失败:" + content)

    def createFramework(self, framework_file_path, plugin, binary_path):
        """
        为插件创建framework
        :param framework_file_path: framework的路径
        :param plugin: 插件名字
        :param binary_path: 插件二进制路径
        """
        # framework_file_path = os.path.join(framework_path, podName + ".framework")
        self.formatter.format_print(framework_file_path)
        if not self.fileHandle.file_exist(framework_file_path):
            self.formatter.format_print(framework_file_path)
            self.shell.excommand_until_done("mkdir -p " + framework_file_path)
        self.shell.excommand_until_done("pwd ")

        self.shell.excommand_until_done("cp -R -p " + binary_path + " " + framework_file_path + "/" + plugin)
        # 创建headers
        dest_headers_path = os.path.join(framework_file_path, "Headers")
        if not self.fileHandle.file_exist(dest_headers_path):
            self.shell.excommand_until_done("mkdir -p " + dest_headers_path)
        headers_source_root = self.arguments.projectPath +"/ios/pluginSource/%s/Classes/" % (plugin)
        file_list = self.fileHandle.myGlob(headers_source_root, True)
        for file in file_list:
            if file.endswith(".h"):
                self.shell.excommand_until_done("cp -R -p " + file + " " + dest_headers_path)

    def processDependency(self, contentDict):
        podName = self.arguments.podName
        dependencyDict = {}  # 支持subspec的时候，需要处理key
        if not contentDict:
            self.result.returnError("打包失败，请查看打包返回结果")
        for key, content in contentDict.items():
            dependency = {}
            contentList = content.split("\n")
            # -> Installing LJGravityImageView (0.1.6)
            for line in contentList:
                if not str(line).startswith("-> Installing "):
                    continue
                contentAndVersionList = line.split(" Installing ")[-1].split(" ")
                if len(contentAndVersionList) != 2:
                    self.result.returnError(line + "\n解析库和版本失败。")
                name = contentAndVersionList[0]
                if podName in name:
                    continue
                version = contentAndVersionList[-1].strip(")").strip("(")
                dependency[name] = version
            if dependency:
                dependencyDict[key] = dependency
        return dependencyDict

    def startPackage(self, subSpecName, debug):
        # 用到的参数
        projectPath = self.arguments.projectPath
        podName = self.arguments.podName
        if subSpecName:
            subspecs = self.podspecTool.subspecList()
        CAFPath = self.arguments.CAFPath
        isFrameWork = self.arguments.framework
        moduleSources = self.arguments.moduleSources
        version = self.arguments.version
        podspecName = podName + subSpecName + ".podspec"
        haveSourceFile = self.podspecTool.canPackage(podName, subSpecName)
        if not haveSourceFile:
            self.formatter.format_warning("没有源码, 不能打这个包 ")
            return "没有源码，打包失败"
        # 打包之前需要先更新repo源。
        moduleSourceList = self.arguments.moduleSourceList
        self.cocoaPodsTool.updateRepoList(moduleSourceList)
        # 备份一份
        self.podspecTool.backUpPodspec()

        # 改变成需要的podspec
        self.podspecTool.changePodSpecForPackage(subSpecName)
        if subSpecName:
            # 创建测试podspec
            self.podspecTool.redirectSubSpec(podName + subSpecName + ".podspec")
            self.cocoaPodsTool.create_tmp_podspec(subSpecName)
        cmd = ""
        # 只有自己的组件是源码，其他的最好是静态库
        if subSpecName and subspecs:
            for subspec in subspecs:
                cmd += podName + "_" + subspec + "_SOURCE=1 "
        else:
            cmd += podName + "_SOURCE=1 "
        if not debug:
            cmd += "IS_RELEASE=1 "
        prefixString = ''
        suffixString = ''
        productDir = podName
        if CAFPath:
            if not self.fileHandle.file_exist(CAFPath):
                self.formatter.format_warning("存放二进制目录不存在，正在创建存放源码二进制的目录")
                self.shell.excommand_until_done("mkdir -p " + CAFPath)
            productDir = os.path.join(CAFPath, podName)
        if isFrameWork:
            cmd += "pod package --verbose " + podspecName + " --force --no-mangle --verbose --exclude-deps --spec-sources="
            suffixString = ".framework"
            productDir = os.path.join(productDir, "Framework")
            cmd += moduleSources + " "
        destFileName = prefixString + podName + suffixString
        if len(subSpecName) > 0:
            productDir += "/" + subSpecName
            destFileName = prefixString + podName + subSpecName + suffixString
            cmd += "--subspecs=" + subSpecName
        productPath = ""
        if debug:
            productDir += "/Debug"
            productPath = productDir + "/" + destFileName
            cmd += " --configuration=Debug "
        else:
            productDir += "/Release"
            productPath = productDir + "/" + destFileName
        cmd += " --archs="+self.arguments.archs + " --archs_sim=" + self.arguments.archs_sim + " "
        self.formatter.format_info(cmd)
        returnCode, content = self.shell.excommand_until_done(cmd)
        if returnCode > 0 or "** BUILD FAILED **" in content or "Build command failed:" in content:
            self.result.returnError("打包失败，请搜索尖括号内 <error: > 或者 <error generated> 或者 <errors generated> 查看具体信息 ")
        self.formatter.format_print(version)
        buildPath = podName + subSpecName + "-" + version
        binaryFilePath = buildPath + "/ios/" + prefixString + podName + subSpecName + suffixString

        if not self.fileHandle.file_exist(productDir):
            self.shell.excommand_until_done("mkdir -p " + productDir)
        else:
            self.shell.excommand_until_done("rm -r -f " + productDir)
            self.shell.excommand_until_done("mkdir -p " + productDir)

        self.formatter.format_print(binaryFilePath)
        if not self.fileHandle.file_exist(binaryFilePath):
            return content
        if haveSourceFile:
            self.formatter.format_print("即将把" + destFileName + "放入发布目录：" + productDir)
            self.shell.excommand_until_done("cp -R -p \"" + binaryFilePath + "\" \"" + productPath + "\"")
            # 创建头文件软链
            self.formatter.format_print("即将把为静态库的创建软链：")
            os.chdir(productDir)
            cmd = "ln -s " + destFileName + "/**/*.h ./"
            self.shell.excommand_until_done(cmd)
            os.chdir(projectPath)

        self.formatter.format_print("即将删除临时文件")
        self.shell.excommand_until_done("rm -r -f " + buildPath)
        self.shell.excommand_until_done("rm -r -f " + podspecName)
        # 恢复最初的 podspec供下次使用
        self.podspecTool.restorePodspec()
        self.formatter.format_info("成功生成静态库")
        return content