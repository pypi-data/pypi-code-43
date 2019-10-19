headers = {
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'Origin': 'https://translate.sogou.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json',
    'Referer': 'https://translate.sogou.com/',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
}

data = {
    'from': 'auto',
    'to': 'zh-CHS',
    'text': 'hello',
    'client': 'pc',
    'fr': 'browser_pc',
    'pid': 'sogou-dict-vr',
    'dict': 'true',
    'word_group': 'true',
    'second_query': 'true',
    'uuid': 'c46a1290-5ad6-4839-975a-21b7ba9a9301',
    'needQc': '1',
    's': '3d52dee36318183131375163cf5f7d78',
}
