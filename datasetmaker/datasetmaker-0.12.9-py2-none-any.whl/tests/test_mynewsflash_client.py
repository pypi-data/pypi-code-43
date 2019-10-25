# mypy: allow-untyped-defs

import unittest
import pandas as pd
from datasetmaker.clients.mynewsflash.countries import identify_countries


class TestCountryIdentification(unittest.TestCase):
    def setUp(self):
        articles = [
            {
                'text': 'Italiens premiärminister har avgått',
                'expected': ['ita']
            },
            {
                'text': 'I Guinea-Bissau regnar det mer än i Guinea.',
                'expected': ['gin', 'gnb']
            },
            {
                'text': 'Amerikanska stridsflygplan i Syrien.',
                'expected': ['syr', 'usa']
            },
            {
                'text': 'I Burma finns burmesiska växter.',
                'expected': ['mmr', 'mmr']
            },
            {
                'text': 'I Myanmar, d.v.s. Burma, finns burmesiska växter.',
                'expected': ['mmr', 'mmr', 'mmr']
            },
            {
                'text': 'Med Kongo avses Kongo-Kinshasa.',
                'expected': ['cod', 'cod']
            },
            {
                'text': 'Med Kongo avses inte Kongo-Brazzaville.',
                'expected': ['cod', 'cog']
            },
            {
                'text': 'Luxemburgs premiärminister besökte Danmark',
                'expected': ['dnk', 'lux']
            },
            # {
            #     'text': 'Polischef Lena Tysk frias från anklagelserna',
            #     'expected': []
            # },
        ]

        self.articles = pd.DataFrame(articles)
        self.identify()

    def identify(self):
        self.articles['identified'] = identify_countries(self.articles['text'])
        self.articles['identified'] = self.articles['identified'].apply(sorted)

    def test_identification(self):
        identified = self.articles['identified'].to_list()
        expected = self.articles['expected'].to_list()
        self.assertSequenceEqual(identified, expected)
