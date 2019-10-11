import re
from typing import List
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup, ResultSet


__all__ = ['GoogleResult', 'GoogleParser']


class GoogleResult:
    def __init__(self, index: int, title: str, link: str):
        self.index = index
        self.title = title
        self.link = link

    @staticmethod
    def create_instance(index: int, block: ResultSet):
        try:
            title = block.find('div', {'class': 'BNeawe vvjwJb AP7Wnd'}).text
            link = unquote(re.search(r'((https|http):\/\/[^&]*)', block.find('a').attrs.get('href'))[0])
            return GoogleResult(
                index,
                title,
                link
            )
        except:
            pass

    def __str__(self):
        return '#{}. {}. Link: {}'.format(
            self.index,
            self.title,
            self.link
        )


class GoogleParser:
    def __init__(self):
        self.links: List[str] = []
        self.body: str = None
        self.non_filtered_links: List[str] = None
        self.links: List[str] = None
        self.bs: BeautifulSoup = None
        self.results: List[GoogleResult] = None

        # SearchParams
        # block class for top of position
        self.top_position_block = 'ZINbbc xpd O9g5cc uUPGi'
        # filtered class, for false position
        self.false_position_block = 'BNeawe vvjwJb AP7Wnd'

    def query(self, search_string):
        link = 'https://google.com/search?q={}'.format(search_string)
        response = requests.get(link)
        self.body = response.content.decode('utf-8', errors='ignore')
        self._get_links_with_soup()
        return self.results

    def _get_links_with_soup(self):
        self.bs = BeautifulSoup(self.body, 'html.parser')
        results = self.bs.find_all('div', {'class': self.top_position_block})
        results = list(filter(lambda i: self.false_position_block in str(i), results))

        self.results = []
        for result in results:
            res = GoogleResult.create_instance(len(self.results) + 1, result)
            if res:
                self.results.append(res)

    def get_str_results(self):
        return [str(res) for res in self.results]


if __name__ == '__main__':
    print(*['\n' + str(res) for res in GoogleParser().query('bitcoin_price')])
