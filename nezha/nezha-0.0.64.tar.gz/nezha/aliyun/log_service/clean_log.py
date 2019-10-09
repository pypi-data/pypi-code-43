"""
# todo
清洗 down_log.sh 下载的日志，通用性不强。
"""
import os
import re

import pandas as pd

THIS_PATH = os.path.abspath(os.path.dirname(__file__))


def clean_downloaded_data() -> None:
    prefix = re.compile('\{".*\sis\s')
    subfix = re.compile('","m.*\}')
    slash_u = re.compile(r'\\\\u')
    cached = []
    with open('{}/downloaded_data.txt'.format(THIS_PATH), encoding='utf-8') as f:
        for i in f.readlines():
            removed_prefix = prefix.sub('', i)
            removed_subfix = subfix.sub('', removed_prefix)
            sub = slash_u.sub(r'\u', removed_subfix)
            cached.append(sub)
    with open('{}/cleaned_downloaded_data.txt'.format(THIS_PATH), encoding='utf-8', mode='w') as f:
        f.writelines(cached)


def cleaned_downloaded_data_turn_2_huizucsv() -> None:
    with open('{}/cleaned_downloaded_data.txt'.format(THIS_PATH), encoding='utf-8') as f:
        pyobj = []
        for i in f.readlines():
            obj = eval(i)
            obj['id_num'] = obj.pop('ident_number')
            pyobj.append(obj)
        df = pd.DataFrame(pyobj)
        print(df)
        df.to_csv('{}/huizu.csv'.format(THIS_PATH), index=False)


if __name__ == '__main__':
    clean_downloaded_data()
    cleaned_downloaded_data_turn_2_huizucsv()
