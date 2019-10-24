import logging
from typing import Union, Any
from pathlib import Path
import requests
import numpy as np
import pandas as pd
from datasetmaker.models import Client
from datasetmaker.datapackage import DataPackage
from datasetmaker.onto.manager import (
    sid_to_id,
    _map)


log = logging.getLogger(__name__)
pd.options.mode.chained_assignment = None


country_name_to_id = _map(entity_name='country', key='name', value='country')


class NobelClient(Client):
    url = 'http://api.nobelprize.org/v1/laureate.json'

    def get(self, **kwargs: Any) -> pd.DataFrame:
        log.info('Fetching data')
        r = requests.get(self.url)
        data = r.json()
        self.data = self.transform(data)
        return self.data

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        drop_cols = ['affiliations', 'share', 'overallMotivation']

        laureates = pd.DataFrame(data['laureates'])
        prizes = pd.io.json.json_normalize(
            data['laureates'], record_path='prizes', meta=['id'])

        prizes = prizes.drop(drop_cols, axis=1, errors='ignore')
        prizes.columns = prizes.columns.map(sid_to_id('nobel'))
        prizes = prizes.dropna(subset=['nobel_category'])
        laureates = laureates.drop(
            ['bornCountryCode', 'diedCountryCode'], axis=1)
        laureates = laureates.rename(columns={
            'id': 'nobel_laureate',
            'born': 'birth.day',
            'bornCity': 'birth.city',
            'bornCountry': 'birth.country',
            'died': 'death.day',
            'diedCity': 'death.city',
            'diedCountry': 'death.country',
            'firstname': 'first_name',
            'surname': 'last_name',
        })

        df = prizes.merge(laureates, on='nobel_laureate')
        df = df.drop('prizes', axis=1)

        df['birth.day'] = df['birth.day'].replace(
            r'\d+-00-00', np.nan, regex=True)
        df['death.day'] = df['death.day'].replace(
            r'\d+-00-00', np.nan, regex=True)
        df['birth.day'] = pd.to_datetime(df['birth.day'])
        df['death.day'] = pd.to_datetime(df['death.day'])

        df['birth.city__name'] = df['birth.city']
        df['death.city__name'] = df['death.city']
        df['birth.city'] = (df['birth.city']
                            .str.strip()
                            .str.replace(r'\s', '_')
                            .str.replace(r',', '')
                            .str.replace(r'\([\w\' ]+\)', '')
                            .str.lower())

        df['death.city'] = (df['death.city']
                            .str.strip()
                            .str.replace(r'\s', '_')
                            .str.replace(r',', '')
                            .str.replace(r'\([\w\' ]+\)', '')
                            .str.lower())

        df['gender'] = df['gender'].replace({'org': None})

        df['birth.country'] = self._clean_country_col(df['birth.country'])
        df['death.country'] = self._clean_country_col(df['death.country'])

        df['birth.city__country'] = df['birth.country']
        df['death.city__country'] = df['death.country']

        df['nobel_instance'] = df.nobel_category.str.cat(df.year, sep='_')
        df['nobel_prize'] = df.nobel_category.str.cat(
            [df.year, df.nobel_laureate], sep='_')

        df['year'] = df.year.astype(int)

        return df

    def _clean_country_col(self, series: pd.Series) -> pd.Series:
        return (series
                .str.replace(r'\([\w\' ]+\)', '')
                .str.replace('W&uuml;rttemberg', 'Württemberg')
                .str.replace('German-occupied Poland', 'Poland')
                .str.strip()
                .str.lower()
                .map(country_name_to_id))

    def save(self, path: Union[Path, str], **kwargs: Any) -> None:
        laureate_props = ['first_name', 'last_name', 'birth.day', 'birth.city', 'birth.country',
                          'death.day', 'death.city', 'death.country', 'gender']
        self.data.ddf.register_entity('nobel_laureate', props=laureate_props)

        self.data.ddf.register_entity('nobel_category')

        self.data.ddf.register_entity('nobel_instance', props=['nobel_category', 'year'])

        self.data.ddf.register_entity('nobel_prize', props=['nobel_laureate',
                                                            'nobel_category',
                                                            'nobel_motivation',
                                                            'year'])

        self.data.ddf.register_entity('country')
        self.data.ddf.register_entity('gender')
        self.data.ddf.register_entity('city')

        log.info('Creating datapackage')
        package = DataPackage(self.data)

        kwargs.update({
            'author': 'Datastory',
            'name': 'nobel',
            'source': 'Nobel Foundation',
            'status': 'draft',
            'title': 'Nobel Foundation',
            'topics': ['science', 'literature', 'economy'],
        })

        package.save(path, **kwargs)
        log.info('Datapackage successfully created')
