import requests
import pandas as pd

class Farfetcher:
    """ API object to fetch listsings."""
    def __init__(self):
        self.base_url = r'https://www.farfetch.com/plpslice/listing-api/products-facets'
        self.headers = {
            'Origin': 'https://www.farfetch.com',
            'Referer': 'https://www.farfetch.com/shopping/m/items.aspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.100 Safari/537.36',
        }
        self.params = '?view={}&pagetype={}&pricetype={}&page={}&gender={}'

    def build_url(self, page=None, view=180, gender='Women', page_type='Shopping', price_type='FullPrice'):
        return self.base_url + self.params.format(view, page_type, price_type, page)

    def listings(self, page=1, gender='Women'):
        response = requests.get(self.build_url(page=page, gender=gender),
                                headers=self.headers)
        return response.json()

    def listings_to_products_dataframe(self, reponse_json):
        return pd.DataFrame.from_dict(response_json['products'])


"""
pagetype

Sets
Shopping
Stories

gender
Women
Men
Kids
"""
