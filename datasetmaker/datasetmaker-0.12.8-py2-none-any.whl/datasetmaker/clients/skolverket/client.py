from typing import Union, Any
from pathlib import Path
import os
import shutil
import logging
from functools import reduce

import requests
import pandas as pd
import numpy as np

from datasetmaker.models import Client
from datasetmaker.datapackage import DataPackage
from datasetmaker.utils import pluck, flatten
from datasetmaker.path import ROOT_DIR

from .MultiYearTable import MultiYearTable
from .concepts import concepts

log = logging.getLogger(__name__)


_base_url = 'https://siris.skolverket.se/siris/reports'
_cache_dir = os.path.join(ROOT_DIR, '.cache_dir')
_form_codes = ['11', '21']  # Grundskolan, Gymnasieskolan


class SkolverketClient(Client):
    _schema: list = []

    def __init__(self) -> None:
        pass

    @property
    def indicators(self) -> list:
        return [x['concept'] for x in concepts if x['concept_type'] == 'measure']  # type: ignore

    def _validate_input(self, indicators: list, years: list) -> None:
        concept_names = pluck(concepts, 'concept')
        for indicator in indicators:
            if indicator not in concept_names:
                raise ValueError(f'{indicator} is not a valid indicator')
            available_years = pluck(self.schema, 'år')
            available_years = [x['kod'] for x in flatten(available_years)]
            for year in years:
                if year not in available_years:
                    raise ValueError(f'{year} is not available in any table')

    def get(self, **kwargs: Any) -> pd.DataFrame:
        indicators: Any = kwargs.get('indicators')
        years: Any = kwargs.get('years')
        cache_dir: Any = kwargs.get('cache_dir')
        if not cache_dir:
            self.cache_dir = Path(_cache_dir)
        else:
            self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        years = [str(x) for x in years]

        # Validate indicators and years
        log.info('Validating indicators and years')
        self._validate_input(indicators, years)

        # Fetch data remotely
        frames = []
        entities = set()
        schemas = self._table_schemas_from_concepts(indicators)
        for schema in schemas:
            _years = [x for x in years if str(x) in pluck(schema['år'], 'kod')]
            log.debug(f'Creating MultiYearTable {schema["kod"]}')
            table = MultiYearTable(schema['kod'], schema['uttag'], _years, self.cache_dir)
            if table.data.empty:
                continue
            frames.append(table.data)
            entities.update(table.entities)
        if not frames:
            return
        keys = list(entities)
        for frame in frames:
            for key in keys:
                if key not in frame:
                    frame[key] = None
        log.info('Merging MultiYearTables')
        # TODO: This try/catch is only for debugging
        try:
            df = reduce(lambda l, r: pd.merge(l, r, on=keys, how='outer'), frames)
        except ValueError:
            print(keys)
            raise
        for indicator in indicators:
            if indicator not in df:
                log.warn(f'{indicator} not in df')

        df = df.filter(items=indicators + keys)

        # Clean data
        log.info('Cleaning data')
        df = df.pipe(self._clean_data)

        self.data = df.set_index(keys)
        return self.data

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.replace(['..', '.'], [None, None])
        df = df.replace(',', '.', regex=True)
        df = df.replace('~100', '100')
        df = df.replace({r'(\d) (\d)': r'\1\2'}, regex=True)

        for col in df.columns:
            if col in [x['concept'] for x in concepts if  # type: ignore
                       x['concept_type'] == 'measure']:  # type: ignore
                df[col] = df[col].astype(np.float64)

        # Standardize these column names
        common = [('skolkod', 'skol_kod'), ('kommunnamn', 'kommun_namn'),
                  ('skolnamn', 'skol_namn'), ('skolnamn', 'skola'),
                  ('program', 'prog'), ('prov', 'provnamn')]

        for i, j in common:
            if j not in df:  # if there are no variables to replace
                continue
            if i not in df:  # if the replacement does not yet exist
                df = df.rename(columns={j: i})
            else:  # if both variables exist
                df[i] = df[i].fillna(df[j])
                df = df.drop(j, axis=1)

        return df

    def clear_cache(self) -> None:
        shutil.rmtree(self.cache_dir)

    @property
    def schema(self) -> list:
        from .api_schema import schema
        return schema
        if self._schema:
            return self._schema
        _schema = []

        for form_code in _form_codes:
            areas_url = (f'{_base_url}/export_api/omrade/'
                         f'?pVerkform={form_code}&pNiva=S')
            areas = requests.get(areas_url).json()

            for area in areas:
                tables_url = (f'{_base_url}/export_api/export/?pVerkform='
                              f'{form_code}&pNiva=S&pOmrade={area["kod"]}')
                tables = requests.get(tables_url).json()

                for table in tables:
                    table['år'] = []
                    years_url = (f'{_base_url}/export_api/lasar/?pExportID='
                                 f'{table["kod"]}')
                    years = requests.get(years_url).json().get('data')

                    for year in years:
                        table['år'].append(year)

                    uttag_url = (f'{_base_url}/export_api/extra/?pExportID='
                                 f'{table["kod"]}&pAr={years[0]["kod"]}')
                    uttag = requests.get(uttag_url).json()
                    if len(uttag['uttag']) == 0:
                        table['uttag'] = 'null'
                    else:
                        table['uttag'] = uttag['uttag'][0]['kod']

                    table.pop('egenskaper')
                    _schema.append(table)
        self._schema = _schema
        return _schema

    def _table_schemas_from_concepts(self, concept_names: list) -> list:
        schemas: list = []
        codes: list = []
        for concept in concept_names:
            table_code = [x['table'] for x in concepts if  # type: ignore
                          x['concept'] == concept][0]  # type: ignore
            schema = [x for x in self.schema if x['kod'] == table_code][0].copy()
            if schema['kod'] not in codes:
                schemas.append(schema)
                codes.append(schema['kod'])
        return schemas

    def save(self, path: Union[Path, str], **kwargs: Any) -> None:
        if self.data.empty:
            raise ValueError('Client has no data')

        kwargs.update({
            'author': 'Datastory',
            'default_measure': 'ak1_elever_tcv6',
            'default_primary_key': ['school_unit', 'year'],
            'name': 'skolverket',
            'source': 'Skolverket',
            'status': 'draft',
            'title': 'Skolverket',
            'topics': ['education'],
        })

        datapoints = []
        entities = []
        for col in self.data.columns:
            data = self.data[col].dropna().reset_index().dropna(axis=1)
            if not data.empty:
                entities.extend(list(data.columns.drop(col)))
                datapoints.append((col, list(data.columns.drop(col))))
        entities = list(set(entities))
        entities.remove('year')

        self.data = self.data.reset_index()
        for entity in entities:
            self.data.ddf.register_entity(entity)
        for datapoint in datapoints:
            self.data.ddf.register_datapoints(datapoint[0], datapoint[1])
        package = DataPackage(self.data)
        package.save(path, **kwargs)
