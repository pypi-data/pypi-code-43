#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import HTMLParser
import cgi
 
def html2py(html_name):
    """
    将图像文件转换为py文件
    :param picture_name:
    :return:
    """
    html_parser = HTMLParser.HTMLParser()
    html = open("%s" % html_name, 'rb')
    html_text = html.read()
    txt = html_parser.unescape(html_text)
    html.close()
    write_data = '%s = "%s"' % ((html_name.split('.')[0]).split('/')[-1],txt)
    f = open('/Users/v-sunweiwei/Desktop//xyscript/xyscript/resource/html/html.py', 'r+')
    date = f.read()
    f = open('/Users/v-sunweiwei/Desktop//xyscript/xyscript/resource/html/html.py', 'w+')
    f.write(date + '\n\r' + write_data)
    f.close()

 
if __name__ == '__main__':
    htmls = ["/Users/v-sunweiwei/Desktop//xyscript/xyscript/resource/html/diagnosemail.html"]
    for i in htmls:
        html2py(i)
