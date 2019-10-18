#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : service-model-dynamic.
# @File         : Receive2Send
# @Time         : 2019-09-03 10:50
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :
import re
import requests
import pandas as pd
from traceback import format_exc
import jieba.analyse as ja
from tqdm import tqdm
from datetime import datetime, timedelta
import time


class DocID(object):

    def __init__(self, debug=False, delta=2, duplicate=True):
        self.debug = debug
        endTime = datetime.today()
        startTime = endTime - timedelta(days=delta)

        self.duplicate = duplicate
        self.url_receive = f'http://c4.admin.browser.miui.srv/panel/api/v1/articleapi/getDocId?cpStatus=1&endTime={str(endTime)[:19]}&startTime={str(startTime)[:19]}'
        self.url_send = 'http://c3.admin.browser.miui.srv/panel/api/v1/articleapi/thridV2'

    def receive(self):
        info_list = []
        for id in tqdm(self.yidian_push_ids, "Receive"):
            try:
                item = self._get_info_yidian(id)
                if item:
                    info_list.append(item)
            except Exception as e:
                print(f"content-not-found: {id}")
                continue

        return pd.DataFrame(info_list).drop_duplicates(['title'])

    def send(self, userPackage, docid_list, topk=3):
        """发送topk"""
        docids = []
        for docid in tqdm(docid_list, 'Send'):
            item = self._get_info(f"http://content.pt.xiaomi.srv/api/v1/contents/{docid}")['item']
            for k in ['keywords', 'extKeywords', 'userTags', 'titleTags']:
                if k in item:
                    keywords = ','.join(item[k])
                    break
                else:
                    keywords = ''
            title = item['title'].strip()  # 人工缩短
            keywords = keywords if keywords else ','.join(ja.tfidf(item['title'], 3, allowPOS=['n', 'vn']))

            if item.get('summary'):
                # subTitle = self._get_newsSummary(item['title'], item['summary'], 128)
                # print(subTitle)
                # subTitle = subTitle if subTitle else item['summary'][:128]
                subTitle = item['summary'][:128]
            else:
                subTitle = item['title']

            pay_load = {"cpStatus": 18,
                        "docIds": "",
                        "duplicate": self.duplicate,
                        "article": [{"docId": docid, "userCategory": userPackage, "subTitle": subTitle, "title": title,
                                     "keywords": keywords}]}

            if self.debug:
                print(pay_load)
            else:
                try:
                    if self.duplicate and len(docids) < topk:
                        r = requests.post(self.url_send, json=pay_load, timeout=10)
                        # print(r.json(encoding="utf8"))
                        docids.append(docid)
                        time.sleep(0.5)
                    else:
                        break
                except Exception as e:
                    print(format_exc().strip())

        print(f"\nPush: {len(docids)} articles")
        return docids

    @property
    def yidian_push_ids(self):
        try:
            return set(self._get_info(self.url_receive, 'POST')['data'])  # 去重
        except Exception as e:
            print(format_exc().strip())

    def _get_info_yidian(self, docid):
        reg = re.compile(r'article/(.*)[?]')
        url = 'http://content.pt.xiaomi.srv/api/v1/contents/'
        print(url + docid)
        info = self._get_info(url + docid)
        if info['item'] is not None and 'push' in info['item']['cpApi']:
            docid = 'yidian_' + reg.findall(info['item']['url'])[0]  # 生成 docid 更新 info
            info = self._get_info(url + docid)

        if info is not None and info['success']:
            return info['item']

    def _get_info(self, url, method='GET'):
        try:
            r = requests.request(method, url, timeout=10)
            if r.json(encoding="utf8")['success']:
                return r.json(encoding="utf8")
        except Exception as e:
            print(format_exc().strip())

    def _get_newsSummary(self, title, text, maxlen=128):
        try:
            url = 'http://web.algo.browser.miui.srv/nlp/bd'
            json = {'method': 'newsSummary', 'text': text, 'title': title, 'maxlen': maxlen}
            r = requests.post(url, json=json, timeout=10).json()
            print(r)
            return r['Score']['summary']
        except Exception as e:
            print(format_exc().strip())


if __name__ == '__main__':
    rs = DocID(False, duplicate=True)
    # print(rs._get_info_yidian('caf464311a06bd4f8ad9dee2b2a9caa2'))
    # print(rs.receive())

    rs.send('xx', ['yidian_V_04Ib5xbA'] * 5)
    # print(rs._get_newsSummary('王者荣耀', '王者荣耀'))
