#!/usr/bin/env python
# -*- coding=utf-8 -*-


from Tools.formatter import Formatter
from Tools.shellCommand import Shell



class Env(object):
    __instance = None

    def __init__(self):
        self.formatter = Formatter.instance()
        self.shell = Shell.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = Env()
        return cls.__instance

    def runtimeEnv(self):
        """
        检查运行环境是否满足
        主要是检查非Python环境的
        :return:
        """
        returnCode, content = self.shell.excommand_until_done("which pip")
        if returnCode > 0:
            self.formatter.format_info("正在安装pip组件（一个类似于gem的安装器")
            self.shell.excommand_until_done("sudo -H easy_install pip")
        returnCode, content = self.shell.excommand_until_done("gem list | grep cocoapods-packager")
        if returnCode > 0:
            self.formatter.format_info("正在安装打包脚本cocoapods-packager, 如果需要改版的packager，请手动安装")
            # 本地的packager
            self.shell.excommand_until_done("sudo -H gem install cocoapods-packager")

