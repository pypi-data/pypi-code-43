# -*- coding: utf-8 -*-
# coding=utf-8
import time
import requests
import urllib.request
from bs4 import BeautifulSoup  # 用于解析HTML
from . import CxExtractor
# import Terry_toolkit as tkit 
# import re

# from __future__ import print_function
# #https://github.com/letiantian/TextRank4ZH
# import sys
# try:
#     reload(sys)
#     sys.setdefaultencoding('utf-8')
# except:
#     pass

# import codecs
# from textrank4zh import TextRank4Keyword, TextRank4Sentence









class CrawlerBaidu:
    """
    # CrawlerBaidu

    抓取百度搜索结果
    
    
    
    """
    '所有员工的基类'
    # empCount = 0

    def __init__(self):
        print('kaishi')
        # self.text = text
        # self.salary = salary
        # Employee.empCount += 1

        # """ 你的 APPID AK SK """

    def get(self, keyword):
        """
        输入关键词获取反馈列表

        >>> get( keyword)

        >>> li = CrawlerBaidu().get('柯基犬')

        >>> print(li)
        
        """
        content_code = urllib.request.quote(keyword)  # 解决中文编码的问题

        url = 'https://www.baidu.com/s?wd=' + content_code
        html = self.open_url(url)
        li = self.get_list(html)
        return li
        pass

    def get_list(self, html):
        """
        获取html中搜索结果

        >>> get_list(html)

        """
        # soup = BeautifulSoup(html, 'lxml')
        soup = BeautifulSoup(html)
        # print(soup)
        # 获取文档对象中“class”属性为“c-showurl”的<a>标签
        # k =
        urls = []
        for result in soup.find_all( class_='result'):
            # print(result)
            print('*'*30)
            # a= result.find_all("a.m").get('href')
            # print(a)
 
            for a in result.find_all(class_='m'):
                 
                print(a.a)
                print('*'*10)
 
            print('*'*100)
            for item in result.find_all('h3'):
                # print(item.a.get_text())
                # print(item.a['href'])
                k = {
                    'title': item.a.get_text(),
                    'url': item.a['href']
                }
                urls.append(k)

        return urls

    def open_url(self, url):
        """
        安全有效的打开url

        >>> open_url(url)
        
        # req = request.build_opener(url)
        # req.add_header(
        #     'User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0')
        # response = urllib.request.urlopen(req)
        # r = requests.get(url)
        # r.status_code
        # r.encoding = 'utf-8'
        # r.text
        # html = response.read().decode('utf8')  # gbk格式的
        # opener = urllib.request.build_opener()
        # opener.addheaders = [('User-agent',  # 添加模拟浏览器访问的header信息
        #                       'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')]
        # html = opener.open(url).read().decode()
        # html = requests.get(url, timeout=10).content.decode('utf-8')


        """
        # print(url)
        req = urllib.request.Request(url)
        req.add_header(
            'User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0')
        response = urllib.request.urlopen(req)

        html = response.read().decode('utf-8')

        return html
    def get_full(self, keyword):
        """
        获取全文搜索结果

        >>> get_full( keyword)

        
        """
        # tr4w = TextRank4Keyword()

        # # tr4w.analyze(text=text, lower=True, window=2)  # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象

        # # print( '关键词：' )
        # # for item in tr4w.get_keywords(20, word_min_len=1):
        # #     print(item.word, item.weight)

        # # print()
        # # print( '关键短语：' )
        # # for phrase in tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2):
        # #     print(phrase)

        # tr4s = TextRank4Sentence()
        # # tr4s.analyze(text=text, lower=True, source = 'all_filters')

        # # print()
        # # print( '摘要：' )
        # # for item in tr4s.get_key_sentences(num=10):
        # #     print(item.index, item.weight, item.sentence)  # index是语句在文本中位置，weight是权重


        li = self.get(keyword)
        cx = CxExtractor.CxExtractor()
        urls = []
        for item in li:

            print(item['title'])
            print(item['url'])

            # test_html = cx.readHtml("E:\\Documents\\123.html")
            # test_html = cx.getHtml(item['url'])
            html = self.open_url(item['url'])
            content = cx.filter_tags(html)
            s = cx.getText(content)
            # print(s)
            k = {
                'title': item['title'],
                'url': item.a['url'],
                'text':s
            }
            urls.append(k)
        return urls
        pass




# li = CrawlerBaidu().get_full('柯基犬')
# print(li)
