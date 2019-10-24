import io
import json
import logging
from typing import Union, Any
from pathlib import Path
import pandas as pd
import numpy as np
import requests
from datasetmaker.datapackage import DataPackage
from datasetmaker.models import Client
from datasetmaker.utils import nice_string
from datasetmaker.merge import merge_packages
from datasetmaker.onto.manager import _map

log = logging.getLogger(__name__)


# Mapping source names to custom short names
snames_to_names = {
    'Utbildningsnivå SUN 2000: eftergymnasial utbildning 3 år eller mer': 'Eftergymnasial utbildning 3+ år',  # noqa
    'Utbildningsnivå SUN 2000: eftergymnasial utbildning mindre än 3 år': 'Eftergymnasial utbildning under 3 år',  # noqa
    'Utbildningsnivå SUN 2000: förgymnasial utbildning': 'Förgymnasial utbildning',
    'Utbildningsnivå SUN 2000: gymnasial utbildning': 'Gymnasial utbildning',
    'Kön och ålder: kvinnor 18-29 år': 'Kvinnor 18-29 år',
    'Kön och ålder: kvinnor 30-49 år': 'Kvinnor 30-49 år',
    'Kön och ålder: kvinnor 50-64 år': 'Kvinnor 50-64 år',
    'Kön och ålder: kvinnor 65+ år': 'Kvinnor 65+ år',
    'Kön och ålder: kvinnor totalt 18+ år': 'Kvinnor 18+ år',
    'Kön och ålder: män 18-29 år': 'Män 18-29 år',
    'Kön och ålder: män 30-49 år': 'Män 30-49 år',
    'Kön och ålder: män 50-64 år': 'Män 50-64 år',
    'Kön och ålder: män 65+ år': 'Män 65+ år',
    'Kön och ålder: män och kvinnor totalt 18-29 år': '18-29 år',
    'Kön och ålder: män och kvinnor totalt 30-49 år': '30-49 år',
    'Kön och ålder: män och kvinnor totalt 50-64 år': '50-64 år',
    'Kön och ålder: män och kvinnor totalt 65+ år': '65+ år',
    'Kön och ålder: män och kvinnor totalt totalt 18+ år': '18+ år',
    'Kön och ålder: män totalt 18+ år': 'Män 18+ år',
    'Kön och ursprung: kvinnor inrikes födda': 'Kvinnor inrikes födda',
    'Kön och ursprung: kvinnor utrikes födda': 'Kvinnor utrikes födda',
    'Kön och ursprung: män inrikes födda': 'Män inrikes födda',
    'Kön och ursprung: män och kvinnor totalt inrikes födda': 'Inrikes födda',
    'Kön och ursprung: män och kvinnor totalt utrikes födda': 'Utrikes födda',
    'Kön och ursprung: män utrikes födda': 'Män utrikes födda',
    'inkomstintervall efter percentiler: 0-20 %': 'Inkomstintervall 0-20 %',
    'inkomstintervall efter percentiler: 21-40 %': 'Inkomstintervall 21-40 %',
    'inkomstintervall efter percentiler: 41-60 %': 'Inkomstintervall 41-60 %',
    'inkomstintervall efter percentiler: 61-80 %': 'Inkomstintervall 61-80 %',
    'inkomstintervall efter percentiler: 81-100 %': 'Inkomstintervall 81-100 %',
    'bostadstyp: eget hem (villa etc.)': 'Bostad: eget hem',
    'bostadstyp: lägenhet, bostadsrätt': 'Bostad: bostadsrätt',
    'bostadstyp: lägenhet, hyresrätt': 'Bostad: hyresrätt',
    'Sverige, 8 grupper: SE06 Norra Mellansverige': 'Norra Mellansverige',
    'Sverige, 8 grupper: SE07+SE08 Mellersta och Övre Norrland (län 22-25)': 'Mellersta och Övre Norrland',  # noqa
    'Sverige, 8 grupper: SE09 Småland med öarna': 'Småland med öarna',
    'Sverige, 8 grupper: SE0A Västsverige': 'Västsverige',
    'Sverige, 8 grupper: SE110 Stockholms län': 'Stockholms län',
    'Sverige, 8 grupper: SE12 Östra Mellansverige': 'Östra Mellansverige',
    'Sverige, 8 grupper: SE2 Södra Sverige': 'Södra Sverige',
    'sektor: kommunalt anställda (kommun samt landsting)': 'Kommunalt anställda (samt landsting)',
    'sektor: privatanställda arbetare': 'Privatanställda arbetare',
    'sektor: privatanställda tjänstemän': 'Privatanställda tjänstemän',
    'sektor: statligt anställda': 'Statligt anställda',
    'fackförbund: LO': 'LO-medlemmar',
    'fackförbund: SACO': 'SACO-medlemmar',
    'fackförbund: TCO': 'TCO-medlemmar',
    'fackförbund: ej fackanslutna': 'Ej fackanslutna',
    'sysselsatt: ej sysselsatta': 'Ej sysselsatta',
    'sysselsatt: sysselsatta': 'Sysselsatta',
}


segments = [
    {
        'title': 'Utbildningsnivå',
        'filters': {'UtbNivaSUN2000': ["F", "3", "K", "L"]},
        'slug': 'Partisympati17'
    },
    {
        'title': 'Kön och ålder',
        'filters': {'Kon': ["1", "2", "TOT"],
                    'Alder': ["18-29", "30-49", "50-64", "65+", "tot18+"]},
        'slug': 'Partisympati051'
    },
    {
        'title': 'Kön och utländsk bakgrund',
        'filters': {'Kon': ["1", "2", "TOT"],
                    'UtrInrFodd': ["110", "113"]},
        'slug': 'Partisympati19'
    },
    {
        'title': 'Inkomstintervall',
        'filters': {'InkomstIntervall': ["0-20", "21-40", "41-60", "61-80", "81-100"]},
        'slug': 'Partisympati081'
    },
    {
        'title': 'Bostadstyp',
        'filters': {'Bostadstyp': ["1", "2", "3"]},
        'slug': 'Partisympati151'
    },
    {
        'title': 'Region',
        'filters': {'Sverige8grupper': ["SE06", "SE07+SE08", "SE09",
                                        "SE0A", "SE110", "SE12", "SE2"]},
        'slug': 'Partisympati101'
    },
    {
        'title': 'Sektor',
        'filters': {'Sektor': ["1", "1C", "4", "5"]},
        'slug': 'Partisympati131'
    },
    {
        'title': 'Fackförbund',
        'filters': {'FackPSU': ["LO", "TCO", "SACO", "ej anslutnaB"]},
        'slug': 'Partisympati141'
    },
    {
        'title': 'Sysselsättningsstatus',
        'filters': {'Sysselsatt': ["SYS", "EJSYS"]},
        'slug': 'Partisympati12'
    },
]


class SCBClient(Client):
    base_url = 'http://api.scb.se/OV0104/v1/doris/sv/ssd/START/ME/ME0201/ME0201B/'

    def get(self, **kwargs: Any) -> pd.DataFrame:
        log.info('Fetching PSU tables')
        dfs = [self._get_psu_table(x['slug'], x['filters']) for x in segments]  # type: ignore

        # Two tables have different column names
        dfs[1] = dfs[1].rename(columns={'parti': 'partisympati'})
        dfs[8] = dfs[8].rename(columns={'parti': 'partisympati'})

        # Two tables have multiple segment columns, merge them
        dfs[1]['Kön och ålder'] = dfs[1]['kön'] + ' ' + dfs[1]['ålder']
        dfs[1] = dfs[1].drop(['kön', 'ålder'], axis=1)
        cols = dfs[1].columns.tolist()
        dfs[1] = dfs[1][cols[-1:] + cols[:-1]]

        dfs[2]['Kön och ursprung'] = dfs[2]['kön'] + ' ' + dfs[2]['utrikes/inrikes född']
        dfs[2] = dfs[2].drop(['kön', 'utrikes/inrikes född'], axis=1)
        cols = dfs[2].columns.tolist()
        dfs[2] = dfs[2][cols[-1:] + cols[:-1]]

        # Concatenate all tables
        log.info('Concatenating PSU tables')
        df = pd.concat([self._reshape_df(x) for x in dfs])

        # Get rid of redundant columns
        df = df[['parti', 'segment', 'alternativ',
                 'månad', 'svarsfördelning', 'felmarginal']]
        df = df.reset_index(drop=True)

        # SCB uses .. for missing values
        df = df.replace('..', np.nan)

        # Cast numeric columns to floats
        df['svarsfördelning'] = df['svarsfördelning'].astype(float)
        df['felmarginal'] = df['felmarginal'].astype(float)

        # Fix date column
        df['datum'] = df['månad'].str.replace('M', '-') + '-01'
        df['datum'] = pd.to_datetime(df['datum'])
        df = df.drop('månad', axis=1)

        # Merge segment names with segment options
        df['scb_psu_pop_segment'] = df['segment'] + ': ' + df['alternativ']
        df['scb_psu_pop_segment__sname'] = df['segment'] + ': ' + df['alternativ']
        df['scb_psu_pop_segment__name'] = df.scb_psu_pop_segment.map(snames_to_names)
        df['scb_psu_pop_segment'] = df.scb_psu_pop_segment.apply(
            nice_string).str.replace(r'\s+', '_').str.replace('-', '_')
        df = df.drop(['segment', 'alternativ'], axis=1)

        # Fix party identifiers
        df.parti = df.parti.replace('övriga', 'oth')
        df.parti = df.parti.str.lower().map(_map('party', 'abbr', 'party', include_synonyms=False))

        # Rename columns
        df = df.rename(columns={
            'svarsfördelning': 'scb_psu_party_sympathy',
            'felmarginal': 'margin_error',
            'datum': 'day',
            'parti': 'party',
        })

        df.day = pd.to_datetime(df.day).dt.strftime('%Y-%m-%d')

        election_results = self._fetch_election_results()

        self.data = [
            {
                'data': df,
                'datapoints': [
                    {
                        'measures': ['scb_psu_party_sympathy', 'margin_error'],
                        'keys': ['party', 'scb_psu_pop_segment', 'day']
                    }
                ],
                'entities': ['party', 'scb_psu_pop_segment']
            },
            {
                'data': election_results,
                'datapoints': [
                    {
                        'measures': ['votes_tot', 'votes_share'],
                        'keys': ['party', 'year']
                    }
                ],
                'entities': ['party']
            }
        ]

        return self.data

    def _fetch_election_results(self) -> pd.DataFrame:
        log.info('Fetching historical election results')
        url = 'http://api.scb.se/OV0104/v1/doris/sv/ssd/START/ME/ME0104/ME0104C/ME0104T3'
        query = {
            'query': [
                {
                    'code': 'Region',
                    'selection': {
                        'filter': 'vs:RegionValkretsTot99',
                        'values': [
                            'VR00'
                        ]
                    }
                }
            ],
            'response': {
                'format': 'json'
            }
        }

        r = requests.post(url, data=json.dumps(query))
        data = json.loads(r.content.decode('utf-8-sig'))

        rows = [x['key'] + x['values'] for x in data['data']]
        df = pd.DataFrame(rows, columns=['region', 'party', 'year', 'votes_tot', 'votes_share'])
        df = df.replace('..', '0')
        df = df.drop('region', axis=1)
        df.party = df.party.str.lower()
        df = df[df.party.isin(['m', 'c', 'fp', 'kd', 'mp', 's', 'v', 'sd', 'övriga'])]
        df.party = df.party.str.replace('övriga', 'oth')
        df.party = df.party.str.replace('fp', 'l')
        df.party = df.party.map(_map('party', 'abbr', 'party', include_synonyms=False))
        df.votes_tot = df.votes_tot.astype(int)
        df.votes_share = df.votes_share.astype(float)
        df.year = df.year.astype(int)
        return df

    def _reshape_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reshapes a dataframe to a common format. Facilitates merging.
        """
        value_vars = [x for x in df.columns if x.startswith(
            'Svarsfördelning') or x.startswith('Felmarginal')]
        id_vars = [x for x in df.columns if not x.startswith(
            'Svarsfördelning') and not x.startswith('Felmarginal')]
        df = pd.melt(df, id_vars=id_vars, value_vars=value_vars)
        df['månad'] = df['variable'].str[-7:]
        df['measurement'] = df['variable'].str.split(',').apply(lambda x: x[0])
        df = df.drop('variable', axis=1)
        df = df.pivot_table(columns='measurement',
                            index=[df.columns[0]] + ['partisympati', 'månad'],
                            values='value',
                            aggfunc='first').reset_index()
        df['segment'] = df.columns[0]
        df = df.rename(columns={df.columns[0]: 'alternativ', 'partisympati': 'parti'})
        df.columns = [x.lower() for x in df.columns]
        return df

    def _create_filter(self, key: str, values: list) -> dict:
        """Helper function to create table filters
        in the JSON format that SCB expects.

        Parameters
        ----------
        key : str
            Filter name, e.g. Kon, Alder, InkomstIntervall
        values : list
            List of values to include for given filter.

        Returns
        -------
        ret : dict
            SCB formatted dictionary with filters.
        """

        return {"code": key, "selection": {"filter": "item", "values": values}}

    def _get_psu_table(self, slug: str, filters: dict) -> pd.DataFrame:
        """Downloads a filtered PSU table.

        Parameters
        ----------
        slug : str
            URL slug to append to base url. Each table has its own slug.
        filters : dict
            Dictionary mapping from filter codes to values to include.

        Returns
        -------
        ret : Pandas dataframe
            The raw table wrapped in a pandas dataframe.
        """

        data = {
            "query": [self._create_filter(x, y) for (x, y) in filters.items()],
            "response": {"format": "csv"}
        }

        url = f'{self.base_url}{slug}'
        r = requests.post(url, data=json.dumps(data))
        return pd.read_csv(io.StringIO(r.text))

    def save(self, path: Union[Path, str], **kwargs: Any) -> None:
        log.info('Creating DataPackage')

        kwargs.update({
            'author': 'Datastory',
            'name': 'scb',
            'source': 'Statistiska Centralbyrån',
            'status': 'draft',
            'title': 'Statistiska Centralbyrån',
            'topics': ['politics', 'sweden'],
        })

        packages: list = []

        for i, data in enumerate(self.data):
            if data['datapoints']:
                for datapoints in data['datapoints']:
                    data['data'].ddf.register_datapoints(**datapoints)
            if data['entities']:
                for entity in data['entities']:
                    data['data'].ddf.register_entity(entity)
            package = DataPackage(data['data'])
            packages.append(package)

        merge_packages(packages, path, **kwargs)

        log.info('Datapackage successfully created')
