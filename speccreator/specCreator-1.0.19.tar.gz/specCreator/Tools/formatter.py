#!/usr/bin/env python
# -*- coding=utf-8 -*-


class Formatter(object):
    """
    格式化类
    """

    __instance = None

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = Formatter()
        return cls.__instance

    def format_print(self, message, separator="", repeatCunt=0):
        if not message:
            return
        if separator:
            print (separator) * repeatCunt
        print str(message)
        if separator:
            print (separator) * repeatCunt + '\n'

    def format_error(self, message):
        """
        打印错误
        :param message: 消息
        """
        self.format_print(message, " *", 40)

    def format_info(self, message):
        """
        打印有站位符的普通消息
        :param message: 消息
        """
        self.format_print(message, " -", 40)

    def format_warning(self, message):
        """
        打印警告
        :param message: 消息
        """
        self.format_print(message, " ?", 40)
