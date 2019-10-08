#!/usr/bin/env python
# -*- coding=utf-8 -*-


import sys
import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
from shellCommand import Shell

sys.getdefaultencoding()

class MDFormatter(object):
    """
    把输出转成markdown文件
    """
    __instance = None

    def __init__(self):
        self.shell = Shell.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = MDFormatter()
        return cls.__instance

    def title(self, title, level=1):
        return "\n" + "#" * level + " " + title + "\n"

    def code(self, code, type="Ruby"):
        """
        把code格式化成markdown的code
        :param code: 源码
        :type code str
        :param type:
        :return:
        """
        content = "\n"
        content += "``` " +  type + "\n"
        content += code
        content += "```"
        content += "\n"
        return content

    def table(self, tablelist, headelist=[]):
        """
        markdown 的表格写法
        :param tablelist:
        :param headelist:
        :return:
        """
        content = "\n"
        if len(headelist) > 0:
            content += "| " + " | ".join(headelist) + " |\n"
        separateList = [":------------:"] * len(headelist)
        content += "|" + " | ".join(separateList) + " |\n"
        # horizontal - vertical
        for hor_list in tablelist:
            content += "|" + " | ".join(hor_list) + " |\n"
        content += "\n"
        return content

    def orderListString(self, list):
        """
        有序列表字符串
        :param list: 列表
        :return:
        """
        content = "\n"
        index = 1
        for line in list:
            content += index + ". " + str(line) + "\n"
            index += 1
        content += "\n"
        return content

    def disorderListString(self, list):
        """
        无序列表
        :param list: 列表
        :return:
        """
        content = "\n"
        for line in list:
            content += "* " + str(line) + "\n"
        content += "\n"
        return content

    def to_html(self, content):
        css = self.css()
        html = markdown.markdown(content, output_format='html5', \
                                 extensions=['markdown.extensions.toc', \
                                             WikiLinkExtension(base_url='https://en.wikipedia.org/wiki/', \
                                                               end_url='#Hyperlinks_in_wikis'), \
                                             'markdown.extensions.sane_lists', \
                                             'markdown.extensions.codehilite', \
                                             'markdown.extensions.abbr', \
                                             'markdown.extensions.attr_list', \
                                             'markdown.extensions.def_list', \
                                             'markdown.extensions.fenced_code', \
                                             'markdown.extensions.footnotes', \
                                             'markdown.extensions.smart_strong', \
                                             'markdown.extensions.meta', \
                                             'markdown.extensions.nl2br', \
                                             'markdown.extensions.tables'])
        html = html.replace("<table>", "<table class=\"table\">")
        return css + html


    def url(self, url, message="链接"):
        """
        markdown 的url
        :param url: 网址
        :param message: 提示信息
        :return:
        """
        return "[" + message + "](" + url + ")"

    def image(self, url, tips=""):
        """
        ![MacDown logo](http://macdown.uranusjr.com/static/images/logo-160.png)
        :param url:
        :return:
        """
        return "![" + tips + "](" + url + ")"

    def bold(self, text):
        """
        粗体
        :param text:
        :return:
        """
        return "**" + text + "**"

    def italic(self, text):
        """
        斜体
        :param text:
        :return:
        """
        return "*" + text + "*"

    def css(self):
        return """
        <style>
    .table table {
        width:100%;
        margin:15px 0;
        border:0;
    }
    .table th {
        background-color:#B8D7FF;
        color:#000000
    }
    .table,.table th,.table td {
        font-size:0.95em;
        text-align:center;
        padding:4px;
        border-collapse:collapse;
    }
    .table th,.table td {
        border: 1px solid #a0c9fe;
        border-width:1px 0 1px 0;
        border:2px outset #ffffff;
    }
    .table tr {
        border: 1px solid #ffffff;
    }
    .table tr:nth-child(odd){
        background-color:#e7f1fe;
    }
    .table tr:nth-child(even){
        background-color:#ffffff;
    }
    </style>
    
        """