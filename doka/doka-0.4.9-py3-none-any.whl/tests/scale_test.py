#!/usr/bin/env python3
import requests

urls = [
    'http://mbagent.ru/kupit-blank-osago-v-moskve/',
    'http://www.evening-kazan.ru/articles/strahovka-po-deshevke-kazancam-prodayut-falshivye-polisy-osago.html',
    'https://blog.goo.ne.jp/pupagifree/e/8ae86ea851556b08229a40ee00a1eb3d?fm=entry_awp_sleep',
    'https://kazanreporter.ru/post/2208_zasada_s_osago',
    'https://lerstrongwind.weebly.com/home/3376263',
    'https://osago-online.tech/osago-optom.html',
    'https://talisman-so.ru/document/formy_dokumientov'
]

for url in urls:
    response = requests.post('http://filter.scaf.icm.local/api/jsonrpc', json={
        "jsonrpc": "2.0",
        "method": "filter.links.avail",
        "id": "4f79ff0e-6cd7-4119-8c88-72ddca5c2d69",
        "params": {
            "url": url
        }
    })

    print(url)
    print(response.json())
