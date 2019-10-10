# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 10:56:09 2019

@author: mayn
"""

from bs4 import BeautifulSoup
import json
import pandas as pd
import math
import re


def ext_jianzhu(page):
    if page is None or page == '':
        return ''
    soup = BeautifulSoup(page, 'html.parser')
    soup_table = soup.table
    trs = soup_table.find_all('tr')
    result = {}
    for tr in trs:
        for td in tr.find_all('td', attrs={'data-header': True}):
            k, v = td['data-header'], td.text.strip()
            result[k] = v
    return json.dumps(result, ensure_ascii=False)


if __name__ == '__main__':
    """
    使用方法：
    from zlparse.zljianzhu.zljianzhu import ext_jianzhu
    
    """
    pass
