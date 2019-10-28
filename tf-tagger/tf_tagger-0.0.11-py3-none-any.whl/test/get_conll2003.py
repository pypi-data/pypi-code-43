#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download CONLL2003 data"""

import os
import requests
from tqdm import tqdm
from appdirs import user_cache_dir

URLS = [
    [
        'conll2003_eng_train.txt',
        'https://raw.githubusercontent.com/deepdialog/NER-datasets/master/CONLL2003/train.txt'
    ],
    [
        'conll2003_eng_valid.txt',
        'https://raw.githubusercontent.com/deepdialog/NER-datasets/master/CONLL2003/valid.txt'
    ],
    [
        'conll2003_eng_test.txt',
        'https://raw.githubusercontent.com/deepdialog/NER-datasets/master/CONLL2003/test.txt'
    ]
]


def main(bioes=True):
    """Download CONLL2003 data and convert it to BIOES format
    B: begin
    I: inner
    E: end
    S: single
    O: out of tag
    """

    cache_dir = user_cache_dir(appname='tf-tagger')
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    for save_path, url in URLS:
        print(save_path)
        res = requests.get(url)
        content = res.text
        part = content.split('\n\n')
        print(len(part))
        all_result = []
        for p in tqdm(part):
            lines = p.split('\n')
            lines = [t.strip() for t in lines if len(t.strip())]
            x = [t.split()[0] for t in lines]
            y = [t.split()[-1] for t in lines]

            nx, ny = [], []
            for i, (xx, yy) in enumerate(zip(x, y)):
                is_last = True if i == (len(x) - 1) else False
                next_yy = None if is_last else y[i + 1]
                if bioes:
                    if yy.startswith('B') and \
                        (is_last or not next_yy.startswith('I')):
                        yy = 'S' + yy[1:]
                    elif yy.startswith('I') and \
                        (is_last or not next_yy.startswith('I')):
                        yy = 'E' + yy[1:]
                nx.append(xx)
                ny.append(yy)
            x, y = nx, ny

            assert len(x) == len(y)
            batch = '\n'.join([
                '{} {}'.format(xx, yy)
                for xx, yy in zip(x, y)
            ])
            all_result.append(batch)
        with open(os.path.join(cache_dir, save_path), 'w') as fobj:
            fobj.write('\n\n'.join(all_result))

if __name__ == '__main__':
    main()
