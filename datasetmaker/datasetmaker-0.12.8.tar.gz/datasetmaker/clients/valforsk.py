import io
import logging
from pathlib import Path
from typing import Union, Any
import pandas as pd
from datasetmaker.models import Client
from datasetmaker.datapackage import DataPackage
from datasetmaker.onto.manager import _map
from datasetmaker.merge import merge_packages
from datasetmaker.utils import get_remote_zip, read_private_github_file

log = logging.getLogger(__name__)


class ValforskClient(Client):
    url = ('https://www.dropbox.com/sh/8hdmg83o0o78ovn/'
           'AABdmOuIgpiOs99IMrgUTsHra?dl=1')

    def get(self, **kwargs: Any) -> list:
        log.info('Fetching remote zip file')
        z = get_remote_zip(self.url)

        mama = pd.read_csv(io.BytesIO(z['trender/utfil_bw15_mama.csv']))
        polls = pd.read_csv(io.BytesIO(z['polls.csv']))
        polls = self._clean_polls(polls)
        mama = self._clean_mama(mama)
        log.info('Reading raw data from Github')
        issues = self._fetch_issues()

        polls.ddf.register_entity('party')
        polls.ddf.register_entity('pollster')
        polls.ddf.register_datapoints(['valforsk_opinion_value', 'valforsk_samplesize'],
                                      ['pollster', 'day'])

        issues.ddf.register_entity('valforsk_issue')
        issues.ddf.register_entity('party')
        issues.ddf.register_datapoints('valforsk_issue_position', [
                                       'valforsk_issue', 'party', 'year'])

        mama.ddf.register_entity('party')
        mama.ddf.register_datapoints('valforsk_mama_est', ['party', 'day'])

        self.data = [polls, issues, mama]
        return self.data

    def _fetch_issues(self) -> pd.DataFrame:
        base_url = 'https://raw.githubusercontent.com/datastory-org/raw-data/master/valforsk/'
        data = 'ddf--datapoints--valforsk_issue_position--by--valforsk_issue--party--year.csv'
        ent = 'ddf--entities--valforsk_issue.csv'
        data_text = read_private_github_file(f'{base_url}{data}').text
        ent_text = read_private_github_file(f'{base_url}{ent}').text
        data_df = pd.read_csv(io.StringIO(data_text))
        ent_df = pd.read_csv(io.StringIO(ent_text))
        data_df.party = data_df.party.map(_map('party', 'abbr', 'party', include_synonyms=False))

        ent_df = ent_df.rename(columns={
            'source': 'valforsk_source',
            'name': 'valforsk_issue__name'
        })

        df = data_df.merge(ent_df, how='left', on='valforsk_issue')
        df = df.dropna(subset=['valforsk_source'])  # Todo: Fix this in data itself
        return df

    def _clean_mama(self, df: pd.DataFrame) -> pd.DataFrame:
        df.date_actual = pd.to_datetime(df.date_actual)
        df['day'] = df.date_actual.dt.strftime('%Y-%m-%d')
        df = df[['day', 'v', 's', 'c', 'l', 'm', 'kd', 'mp', 'sd', 'oth', 'dk']]
        df = df.melt(id_vars='day', var_name='party', value_name='valforsk_mama_est')
        df.party = df.party.map(_map('party', 'abbr', 'party', include_synonyms=False))
        df.valforsk_mama_est = df.valforsk_mama_est.round(3)
        return df

    def _clean_polls(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean dataframe with raw polling data"""

        # Drop error rows
        df = df[df.coll_per_start.notnull()]
        df = df[df.coll_per_end.notnull()]

        # Calculate date between start an end
        df.coll_per_start = pd.to_datetime(df.coll_per_start)
        df.coll_per_end = pd.to_datetime(df.coll_per_end)
        polls_length = df.coll_per_end - df.coll_per_start
        df['day'] = (df.coll_per_start + (polls_length / 2)).dt.strftime('%Y-%m-%d')

        # Drop redundant columns
        df = df.drop(['coll_per_start', 'coll_per_end'], axis=1)

        # Melt party columns
        party_cols = ['m', 'l', 'c', 'kd', 's', 'v',
                      'mp', 'sd', 'fi', 'pp', 'oth', 'dk']
        df = df.melt(id_vars=['pollster', 'day', 'samplesize'],
                     value_vars=party_cols,
                     var_name='party',
                     value_name='valforsk_opinion_value')

        df = df.rename(columns={'samplesize': 'valforsk_samplesize'})
        df.pollster = df.pollster.str.lower()
        df.party = df.party.map(_map('party', 'abbr', 'party', include_synonyms=False))

        return df

    def save(self, path: Union[Path, str], **kwargs: Any) -> None:

        log.info('Creating datapackage')

        kwargs.update({
            'author': 'Datastory',
            'default_measure': 'valforsk_opinion_value',
            'default_primary_key': ['pollster', 'day', 'party'],
            'name': 'valforskningsprogrammet',
            'source': 'Valforskningsprogrammet',
            'status': 'published',
            'title': 'Valforskningsprogrammet',
            'topics': ['politics', 'sweden'],
        })

        packages = [DataPackage(x) for x in self.data]
        merge_packages(packages, path, **kwargs)

        log.info('Datapackage successfully created')
