import logging
from typing import Union, Any
from pathlib import Path
import pandas as pd
from datasetmaker.datapackage import DataPackage
from datasetmaker.merge import merge_packages
from datasetmaker.models import Client
from datasetmaker.onto.manager import _map

log = logging.getLogger(__name__)


class SIPRI(Client):
    url = ('https://www.sipri.org/sites/default'
           '/files/SIPRI-Milex-data-1949-2018_0.xlsx')

    def get(self, **kwargs: Any) -> list:
        df = pd.read_excel(self.url,
                           engine='openpyxl',
                           sheet_name=None,  # all sheets
                           na_values=['. .', '..', 'xxx'])
        df_milexp_cap = self._parse_milexp_cap(df['Per capita'].copy())
        df_milexp_gov = self._parse_milexp_gov(
            df['Share of Govt. spending'].copy())
        df_milexp_locc_fin_years = self._parse_milexp_locc_fin_years(
            df['Local currency financial years'].copy())
        df_milexp_locc_cal_years = self._parse_milexp_locc_cal_years(
            df['Local currency calendar years'].copy())
        df_milexp_const = self._parse_milexp_const(
            df['Constant (2017) USD'].copy())
        df_milexp_cur = self._parse_milexp_cur(
            df['Constant (2017) USD'].copy())
        df_milexp_gdp = self._parse_milexp_gdp(df['Share of GDP'].copy())

        self.data = [
            {
                'data': df_milexp_cap,
                'datapoints': [['sipri_milexp_cap'], ['country', 'year']],
                'entities': ['country']
            },
            {
                'data': df_milexp_gov,
                'datapoints': [['sipri_milexp_gov'], ['country', 'year']],
                'entities': ['country']
            },
            {
                'data': df_milexp_locc_fin_years,
                'datapoints': [['sipri_milexp_locc_fin_years'],
                               ['country', 'year', 'sipri_currency']],
                'entities': ['country', 'sipri_currency']},
            {
                'data': df_milexp_locc_cal_years,
                'datapoints': [['sipri_milexp_locc_cal_years'],
                               ['country', 'year', 'sipri_currency']],
                'entities': ['country', 'sipri_currency']},
            {
                'data': df_milexp_const,
                'datapoints': [['sipri_milexp_const'], ['country', 'year']],
                'entities': ['country']},
            {
                'data': df_milexp_cur,
                'datapoints': [['sipri_milexp_cur'], ['country', 'year']],
                'entities': ['country']},
            {
                'data': df_milexp_gdp,
                'datapoints': [['sipri_milexp_gdp'], ['country', 'year']],
                'entities': ['country']
            },
        ]

        return self.data

    def _parse_milexp_gdp(self, sheet: pd.DataFrame) -> pd.DataFrame:
        """
        Parse military expenditure as percentage of GDP sheet.
        """
        sheet.columns = sheet.iloc[4]
        sheet.columns = [str(x).strip() for x in sheet.columns]
        sheet = sheet.drop([x for x in sheet.columns if x == 'nan'], axis=1)
        sheet = sheet.drop(
            [x for x in sheet.columns if 'Current' in x], axis=1)
        sheet = sheet[5:]

        sheet = (sheet
                 .set_index('Country')
                 .drop(['Notes'], axis=1)
                 .dropna(how='all', axis='rows')
                 .reset_index()
                 .melt(id_vars=['Country'],
                       var_name='year',
                       value_name='sipri_milexp_gdp'))

        sheet.Country = sheet.Country.str.replace(
            'Norh Macedonia', 'North Macedonia')
        sheet.Country = sheet.Country.str.replace(
            'Congo, Repubic of', 'Congo, Republic of')

        sheet.columns = [x.lower() for x in sheet.columns]
        sheet.country = sheet.country.str.lower().str.strip()
        sheet.country = sheet.country.map(_map('country', 'name', 'country'))
        sheet.year = sheet.year.astype(float).astype(int)
        sheet = sheet.dropna(subset=['sipri_milexp_gdp'])
        return sheet

    def _parse_milexp_cur(self, sheet: pd.DataFrame) -> pd.DataFrame:
        """
        Parse military expenditure in current million USD sheet.
        """
        sheet.columns = sheet.iloc[4]
        sheet.columns = [str(x).strip() for x in sheet.columns]
        sheet = sheet.drop([x for x in sheet.columns if x == 'nan'], axis=1)
        sheet = sheet.drop(
            [x for x in sheet.columns if 'Current' in x], axis=1)
        sheet = sheet[5:]

        sheet = (sheet
                 .set_index('Country')
                 .drop(['Notes'], axis=1)
                 .dropna(how='all', axis='rows')
                 .reset_index()
                 .melt(id_vars=['Country'],
                       var_name='year',
                       value_name='sipri_milexp_cur'))

        sheet.columns = [x.lower() for x in sheet.columns]
        sheet.country = sheet.country.str.lower().str.strip()
        sheet.country = sheet.country.map(_map('country', 'name', 'country'))
        sheet.year = sheet.year.astype(float).astype(int)
        sheet = sheet.dropna(subset=['sipri_milexp_cur'])
        return sheet

    def _parse_milexp_locc_fin_years(self, sheet: pd.DataFrame) -> pd.DataFrame:
        """
        Parse military expenditure in local currency financial years sheet.
        """
        sheet.columns = sheet.iloc[6]
        sheet.columns = [str(x).strip() for x in sheet.columns]
        sheet = sheet[7:]

        sheet = (sheet
                 .set_index('Country')
                 .drop(['Notes', 'Fiscal Year (Jan-Dec if not stated)'],
                       axis=1)
                 .dropna(how='all', axis='rows')
                 .reset_index()
                 .melt(id_vars=['Country', 'Currency'],
                       var_name='year',
                       value_name='sipri_milexp_locc_fin_years'))

        sheet.Currency = sheet.Currency.str.strip()
        sheet.columns = [x.lower() for x in sheet.columns]
        sheet = sheet.rename(columns={'currency': 'sipri_currency'})
        sheet.country = sheet.country.str.lower().str.strip()
        sheet.country = sheet.country.map(_map('country', 'name', 'country'))
        sheet.year = sheet.year.astype(float).astype(int)
        sheet = sheet.dropna(subset=['sipri_milexp_locc_fin_years'])
        return sheet

    def _parse_milexp_locc_cal_years(self, sheet: pd.DataFrame) -> pd.DataFrame:
        """
        Parse military expenditure in local currency calendar years sheet.
        """
        sheet.columns = sheet.iloc[5]
        sheet.columns = [str(x).strip() for x in sheet.columns]
        sheet = sheet[6:]
        # Below line needed due to hidden text in Excel file...
        sheet = sheet[~sheet.Country.str.contains('igures for', na=False)]

        sheet = (sheet
                 .set_index('Country')
                 .drop(['Notes'], axis=1)
                 .dropna(how='all', axis='rows')
                 .dropna(how='all', axis='columns')
                 .reset_index()
                 .melt(id_vars=['Country', 'Currency'],
                       var_name='year',
                       value_name='sipri_milexp_locc_cal_years'))

        sheet.columns = [x.lower() for x in sheet.columns]
        sheet = sheet.rename(columns={'currency': 'sipri_currency'})
        sheet.country = sheet.country.str.lower().str.strip()
        sheet.country = sheet.country.map(_map('country', 'name', 'country'))
        sheet.year = sheet.year.astype(float).astype(int)
        sheet = sheet.dropna(subset=['sipri_milexp_locc_cal_years'])
        return sheet

    def _parse_milexp_const(self, sheet: pd.DataFrame) -> pd.DataFrame:
        """Parse military expenditure in constant USD sheet."""
        sheet.columns = sheet.iloc[4]
        sheet.columns = [str(x).strip() for x in sheet.columns]
        sheet = sheet.drop([x for x in sheet.columns if x == 'nan'], axis=1)
        sheet = sheet.drop(
            [x for x in sheet.columns if 'Current' in x], axis=1)
        sheet = sheet[5:]

        sheet = (sheet
                 .set_index('Country')
                 .drop('Notes', axis=1)
                 .dropna(how='all', axis='rows')
                 .reset_index()
                 .melt(id_vars=['Country'],
                       var_name='year',
                       value_name='sipri_milexp_const'))

        sheet.columns = [x.lower() for x in sheet.columns]
        sheet.country = sheet.country.str.lower().str.strip()
        sheet.country = sheet.country.map(_map('country', 'name', 'country'))
        sheet.year = sheet.year.astype(float).astype(int)
        sheet = sheet.dropna(subset=['sipri_milexp_const'])
        return sheet

    def _parse_milexp_cap(self, sheet: pd.DataFrame) -> pd.DataFrame:
        """Parse military expenditure per capita sheet."""
        sheet.columns = sheet.iloc[5]
        sheet = (sheet
                 .drop(5)
                 .set_index('Country')
                 .drop('Notes', axis=1).dropna(how='all', axis='rows')
                 .reset_index()
                 .melt(id_vars=['Country'],
                       var_name='year',
                       value_name='sipri_milexp_cap'))

        sheet.columns = [x.lower() for x in sheet.columns]
        sheet.country = sheet.country.str.lower().str.strip()
        sheet.country = sheet.country.map(_map('country', 'name', 'country'))
        sheet.year = sheet.year.astype(int)
        sheet = sheet.dropna(subset=['sipri_milexp_cap'])
        return sheet

    def _parse_milexp_gov(self, sheet: pd.DataFrame) -> pd.DataFrame:
        """
        Parse military expenditure as percentage
        of government spending sheet.
        """
        sheet.columns = sheet.iloc[6]
        sheet = sheet[7:]

        sheet = (sheet
                 .set_index('Country')
                 .drop(['Notes', 'Reporting year'], axis=1)
                 .dropna(how='all', axis='rows')
                 .reset_index()
                 .melt(id_vars=['Country'],
                       var_name='year',
                       value_name='sipri_milexp_gov'))

        sheet.columns = [x.lower() for x in sheet.columns]
        sheet.country = sheet.country.str.lower().str.strip()
        sheet.country = sheet.country.map(_map('country', 'name', 'country'))
        sheet.year = sheet.year.astype(int)
        sheet = sheet.dropna(subset=['sipri_milexp_gov'])
        return sheet

    def save(self, path: Union[Path, str], **kwargs: Any) -> None:

        log.info('Creating datapackage')

        kwargs.update({
            'author': 'Datastory',
            'default_measure': 'sipri_milexp_cap',
            'default_primary_key': ['country', 'year'],
            'name': 'sipri',
            'source': 'Sipri',
            'status': 'draft',
            'title': 'Sipri',
            'topics': ['military'],
        })

        packages = list()

        for i, data in enumerate(self.data):
            if data['datapoints']:
                data['data'].ddf.register_datapoints(data['datapoints'][0], data['datapoints'][1])
            if data['entities']:
                for entity in data['entities']:
                    data['data'].ddf.register_entity(entity)
            package = DataPackage(data['data'])
            packages.append(package)

        merge_packages(packages, path, **kwargs)

        log.info('Datapackage successfully created')
