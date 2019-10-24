import requests
import sys
from bs4 import BeautifulSoup as BS


def get_info():
    word = sys.argv[1]
    base_url = 'http://dict.youdao.com'
    url = 'http://dict.youdao.com/w/eng/'+word
    html = requests.get(url).text
    sp = BS(html, 'lxml')

    # 基本解释
    explanation = sp.find(class_='trans-container').find_all('li')
    for item in explanation:
        print(str(item)[4:-5])

    # 例句
    print('\nCollins Dictionary examples:')
    for every in sp.find_all(class_='examples'):
        ls = every.find_all('p')
        for item in ls:
            print(str(item)[4:-4])

    # 更多例句
    print("\n\nfor more examples:")
    url_more_examples = sp.find_all(class_='more-example')[0].attrs['href']
    print(base_url+url_more_examples)
