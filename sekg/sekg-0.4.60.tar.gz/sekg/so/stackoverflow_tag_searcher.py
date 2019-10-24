# # -*-coding:utf-8-*-
import os
import pickle
import urllib
import time
import gensim
import requests
from bs4 import BeautifulSoup
import zipfile
from xml.etree.ElementTree import parse
from pathlib import Path
from sekg.util.annotation import catch_exception

from sekg.so.SOTagItem import SOTagItem


class SOTagSearcher(gensim.utils.SaveLoad):
    maxTryNum = 5
    user_agent = {"user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; SV1; .NET CLR 1.1.4322)"}

    def __init__(self):
        self.tag_info_cache = self.__int_tags()
        self.synonyms_dic = {}

    @catch_exception
    def __int_tags(self):
        if os.path.exists('./stackoverflow.com-Tags.zip'):
            with zipfile.ZipFile('./stackoverflow.com-Tags.zip', 'r') as z:
                f = z.open('Tags.xml')
            doc = parse(f)
            root = doc.getroot()
            tag_data = []
            for child in root:
                tag_data.append(child.attrib)
            tag_dic = {}
            for item in tag_data:
                tag_dic[item["TagName"].lower()] = SOTagItem(tag_info_dic=item)
            return tag_dic
        else:
            return {}

    def __update_synonyms_dic(self, tag, synonyms_set):
        if synonyms_set:
            for tag_syn in synonyms_set:
                self.synonyms_dic[tag_syn] = tag

    def parse_synonyms(self, html):
        if html:
            soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
            div = soup.find('div', class_="mainbar")
            syn_set = set()
            if div:
                a_list = div.find_all('a', class_="post-tag")
                for item in a_list:
                    syn_set.add(item.text)
            return syn_set
        else:
            return set()

    def parse_tag_info(self, html):
        short_text = ""
        long_text = ""
        if html:
            soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
            text_div = soup.find('div', class_='post-text')
            short_div = text_div.find('div', class_="welovestackoverflow")
            if short_div:
                p = short_div.find('p')
                short_text = p.text
            long_text = ""
            while True:
                item = short_div.find_next_sibling()
                item_current = str(item)
                if item_current.startswith("<p>"):
                    long_text += item.text + "\n"
                    short_div = item
                else:
                    break
            return short_text, long_text
        else:
            return short_text, long_text

    def download_html(self, url):
        try:
            html = requests.get(url, headers=self.user_agent).content
            if html:
                return html
            else:
                return ""
        except urllib.error.URLError as e:
            if hasattr(e, "code"):
                print(e.code)
            if hasattr(e, "reason"):
                print(e.reason)

    def __fetch_synonyms_for_one_tag(self, tag):
        try:
            url = 'https://stackoverflow.com/tags/' + tag + "/synonyms"
            # print("url now: ", url)
            for tries in range(self.maxTryNum):
                html = self.download_html(url)
                if not html:
                    print("Dear Host,I can not find the web page for tag", tag)
                else:
                    parse_result = self.parse_synonyms(html)
                    if parse_result:
                        synonyms = parse_result - {tag}
                        self.__update_synonyms_dic(tag, synonyms)
                        return synonyms
            return {}
        except urllib.error.URLError as e:
            if hasattr(e, "code"):
                print(e.code)
            if hasattr(e, "reason"):
                print(e.reason)
            time.sleep(10)
        except Exception as e:
            print("exception:" + str(e))
            time.sleep(10)

    def __fetch_tag_info_for_one_tag(self, tag):
        try:
            url = 'https://stackoverflow.com/tags/' + tag + "/info"
            # print("url now: ", url)
            for tries in range(self.maxTryNum):
                html = self.download_html(url)
                if not html:
                    print("Dear Host,I can not find the web page for tag", tag)
                else:
                    short_text, long_text = self.parse_tag_info(html)
                    if short_text or long_text:
                        return short_text, long_text, html
            return "", "", ""
        except urllib.error.URLError as e:
            if hasattr(e, "code"):
                print(e.code)
            if hasattr(e, "reason"):
                print(e.reason)
            time.sleep(10)
        except Exception as e:
            print("exception:" + str(e))
            time.sleep(10)
        pass

    def get_tag_item_for_one_tag(self, tag):
        tag = tag.lower()
        if tag in self.tag_info_cache.keys():
            if self.tag_info_cache[tag].is_valid():
                return self.tag_info_cache[tag]
            else:
                short_text, long_text, info_html = self.__fetch_tag_info_for_one_tag(tag)
                synonyms = self.__fetch_synonyms_for_one_tag(tag)
                tag_item = self.tag_info_cache[tag]
                tag_item.update_short_description(short_text)
                tag_item.update_long_description(long_text)
                tag_item.update_info_html(info_html)
                tag_item.update_tag_synonyms(synonyms)
                self.tag_info_cache[tag] = tag_item
                return tag_item
        else:
            if tag in self.synonyms_dic.keys():
                new_tag = self.synonyms_dic[tag]
                return self.tag_info_cache[new_tag]
            return None

    def get_tag_item(self, tags):
        return_tag_data = {}
        for tag in tags:
            tag = tag.lower()
            tag_item = self.get_tag_item_for_one_tag(tag)
            if tag_item:
                return_tag_data[tag] = tag_item
        return return_tag_data

    def run(self):
        for tag_name in self.tag_info_cache.keys():
            self.get_tag_item_for_one_tag(tag_name)
        return self.tag_info_cache

    def get_tag_info_cache(self):
        return self.tag_info_cache

    def __repr__(self):
        return "<AsyncWikiSearcher tags_count=%r>" % (len(self.tag_info_cache))
