#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AIPipeline.
# @File         : DocRecall
# @Time         : 2019-09-12 10:25
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  : 

import pandas as pd
from concurrent.futures import ThreadPoolExecutor


class ItemRecall(object):
    """https://wiki.n.miui.com/pages/viewpage.action?pageId=138343970"""

    def __init__(self):
        pass

    def item_list(self, queues=["cmshot", 'historyhighctr', 'topnewsctr', 'hotchannel']):
        with ThreadPoolExecutor(8) as pool:
            df = pd.concat(pool.map(self._get_docid, queues, timeout=10))
            return df.iloc[:, 1].drop_duplicates().to_list()

    def _get_docid(self, queue='cmshot'):
        try:
            url = f"http://web.algo.browser.miui.srv/data/feed/recall?q={queue}"
            df = pd.read_html(url, encoding='utf-8')[0].iloc[:, [1, 10]]
        except Exception as e:
            print(e)
            df = pd.DataFrame()
        return df


if __name__ == '__main__':
    print(ItemRecall()._get_docid())
    print(ItemRecall().item_list())
