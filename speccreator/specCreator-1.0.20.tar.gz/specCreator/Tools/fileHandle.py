#!/usr/bin/env python
# -*- coding=utf-8 -*-

import os
import time
import sys
import glob
import fcntl
import yaml
from formatter import Formatter


class FileHandle(object):

    __instance = None

    def __init__(self):
        self.formater = Formatter.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = FileHandle()
        return cls.__instance

    def newFileName(self, fileName, suffix):
        """文件重命名
        Arguments:
            fileName {string} -- 文件名
        Returns:
            string -- 重命名后的文件名
        """
        if '/' in fileName:
            return "_".join(fileName.split("/")) + suffix
        else:
            return fileName + suffix


    def newCookieFileName(self, webServer, suffix='.cookie'):
        """
        返回webServer的cookie名字
        Arguments:
            webServer {str} -- 访问的webServer
        Keyword Arguments:
            suffix {str} -- 后缀 (default: {'.cookie'})
        Returns:
            [str] -- 新的cookie名字
        """
        return self.newFileName(webServer, suffix)

    def newCacheFileName(self, fileName, suffix='.cache'):
        """
        返回缓存文件的名字
        Arguments:
            fileName {string} -- 原文件名
        Returns:
            string -- 缓存文件名
        """
        return self.newFileName(fileName, suffix)

    def newLogFileName(self, fileName, suffix='_diff.log'):
        """
        获取log文件的文件名
        Arguments:
            fileName {string} -- log文件名
        Returns:
            string -- [description]
        """
        return self.newFileName(fileName, suffix)


    def urlCacheFilePath(self, url, suffix='.cache'):
        """
        获取url缓存后的路径
        Arguments:
            url {string} -- url

        Returns:
            string -- 文件名
        """
        cacheFileName = self.newCacheFileName(url, suffix)
        filePath = self.file_path + "/" + cacheFileName
        return filePath

    def getFileCreateTime(self, filePath):
        """
        获取文件创建时间
        Arguments:
            filePath {str} -- 文件路径
        Returns:
            int -- 时间戳
        """
        filePath = unicode(filePath, 'utf8')
        t = os.path.getctime(filePath)
        return int(t)

    def getCurrentTime(self, filePath):
        "返回当前时间戳"
        return int(time.time())

    def versionHistoryPath(self, podName, url, LJurlPrefix):
        """返回更新文档的位置
        Arguments:
            podName {str} -- 库名
            url {str} -- 库的git地址
            LJurlPrefix {str} -- 链家库的前缀
        Returns:
            str -- 更新文档路径
        """

        versionHistoryPath = url
        if url.startswith(LJurlPrefix):
            # 是链家的
            versionHistoryPath += "/raw/master/"
            if url.split('/')[-1] != podName:
                versionHistoryPath += podName
            versionHistoryPath += "/VersionHistory.md"
        else:
            # 不是链家的
            versionHistoryPath += "/releases"
        return versionHistoryPath

    def fileOverDue(self, filePath, overTime):
        """
        判断文件是否过期
        Arguments:
            filePath {str} -- 文件路径
            overTime {int} -- 过期时间
        Returns:
            bool -- 是否过期
        """
        if self.getCurrentTime(filePath) - self.getFileCreateTime(filePath) - overTime >= 0:
            return True
        else:
            return False

    def readLines(self, filePath):
        """[按行读取文件的全部内容，返回数组]

        Arguments:
            filePath {string} -- 文件名

        Returns:
            List -- 每一行的数组
        """
        with open(filePath, "r") as file:
            return file.readlines()

    def isfile(self, fileName):
        """
        判断当前工程目录下有没有这个文件
        Arguments:
            fileName {String} -- fileName
        Returns:
            bool -- 文件是否存在
        """
        if os.path.isfile(fileName):
            return True
        else:
            return False

    def isDir(self, fileName):
        """
        判断是不是目录
        Arguments:
            fileName {String} -- fileName
        Returns:
            bool -- 文件是否存在
        """
        if os.path.isdir(fileName):
            return True
        else:
            return False

    def file_exist(self, filePath):
        """
        判断文件是否存在
        :param filePath: 文件目录
        :return:
        """
        if os.path.exists(filePath):
            return True
        else:
            return False

    def delTempFiles(self, fileList):
        """删除临时文件
        Arguments:
            fileList {List} -- 临时文件列表
        """
        self.formater.format_print("临时文件列表为：" + str(fileList))
        for fileName in fileList:
            logFilePath = fileName
            if os.path.isfile(logFilePath):
                self.formater.format_print('正在删除临时文件' + logFilePath)
                os.remove(logFilePath)
            elif os.path.isdir(logFilePath):
               self.formater.format_print('文件夹暂时不允许删除')

    def writeToFile(self, string, filePath):
        """
        把内容写进文件,线程安全
        Arguments:
            string {string} -- 文件内容
            filePath {string} -- 文件路径
        """
        with open(filePath, "w+") as fileWriter:
            fcntl.flock(fileWriter, fcntl.LOCK_EX)
            fileWriter.write(string)
            fileWriter.flush()
            fcntl.flock(fileWriter, fcntl.LOCK_UN)

    def appendToFile(self, string, filePath):
        with open(filePath, "a+") as fileWriter:
            fileWriter.write(str(string))

    def writeYamlToFile(self, string, filePath):
        """
        把 内容写进yaml文件
        :param string: 文件内容
        :param filePath: 文件路径
        :return:
        """
        with open(filePath, "w+") as fileWriter:
            fcntl.flock(fileWriter, fcntl.LOCK_EX)
            yaml.dump(string, fileWriter)
            fcntl.flock(fileWriter, fcntl.LOCK_UN)

    def readFile(self, filePath):
        """
        读取文件内容
        :param filePath: 文件路径
        :return:
        """
        with open(filePath, "r+") as fileReader:
            return fileReader.read()

    def readYamlFile(self, filePath):
        """
        读取yaml文件
        :param filePath: 文件路径
        :return:
        """
        with open(filePath, "r+") as fileReader:
            return yaml.load(fileReader.read())

    def removeFile(self, filePath):
        if self.file_exist(filePath):
            try:
                os.remove(filePath)
            except IOError:
                print ('系统错误，无法删除文件-' + filePath + '，可能被占用')
                # 清空
                self.writeToFile("", filePath)

    def myGlob(self, path, recursion=False):
        fileList = []
        for fileName in os.listdir(path):
            fileDir = os.path.join(path, fileName)
            # nestBasename = os.path.join(fileDir, fileName)
            if os.path.isdir(fileDir):
                if recursion:
                    nextFileList = self.myGlob(fileDir, recursion)
                    if nextFileList:
                        fileList.extend(nextFileList)
            else:
                fileList.append(fileDir)
        return list(set(fileList))

