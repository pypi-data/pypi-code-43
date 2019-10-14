from typing import Optional, Union, Any
from pathlib import Path
import logging
import pandas as pd
import ddf_utils
from datasetmaker.models import Client
from datasetmaker.utils import S3DataStore, stretch, nice_string
from datasetmaker.onto.manager import _map
from datasetmaker.datapackage import DataPackage
from datasetmaker.merge import merge_packages
from .download import NewsFetcher
from .corpus import ArticleDropper
from .countries import identify_countries

log = logging.getLogger(__name__)


class MyNewsFlashClient(Client):
    _default_ts = pd.Timestamp('2019-08-01T00:00:01+00:00')

    def get(self, append_to: Optional[str] = None) -> pd.DataFrame:
        """
        Get news articles.

        Parameters
        ----------
        append_to : {str, pathlib.Path}
            Path to existing datapackage. If supplied, appends only missing days.
        """
        self.datastore = S3DataStore()
        log.info('Syncing remote data store')
        self._sync_data_store()

        if append_to:
            log.info('Reading timestamp of existing local package')
            ddf_path = Path(append_to)
            pkg_ts = pd.Timestamp(ddf_utils.package.get_datapackage(ddf_path)['created'])
        else:
            pkg_ts = self._default_ts

        time_key = f'{str(pkg_ts.year)}-{str(pkg_ts.month).zfill(2)}'
        raw_files = self.datastore.list_files_in_folder('', suffix='csv')
        to_process = [x for x in raw_files if Path(x).stem >= time_key]
        log.info(f'Preparing to process {len(to_process)} raw files')
        df = self._identify_countries([self.datastore.read_csv(x) for x in to_process])

        log.info('Creating articles dataframe')
        articles = self._create_articles(df)

        log.info('Creating country counts dataframe')
        counts = self._count_countries(df)
        counts = counts[['country', 'day', 'swe_media_mentions']]
        counts = counts.sort_values(['day', 'country'])

        self.data = [
            {'data': counts, 'datapoints': [['swe_media_mentions'], ['country', 'day']]},
            {'data': articles, 'datapoints': []}
        ]
        return self.data

    def _create_articles(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[['headline', 'source', 'indexed', 'url', 'countries']]
        df['day'] = df.indexed.dt.strftime('%Y%m%d')
        df = df.drop('indexed', axis=1)
        df = stretch(df,
                     index_col=['day', 'source', 'headline', 'url'],
                     value_col='countries',
                     sep=',')
        df = df.rename(columns={
            'source': 'media_org',
            'countries': 'country',
        })
        df.media_org = df.media_org.str.replace(' - Ekot', '').str.strip()
        df.media_org = df.media_org.map(_map('media_org', 'name', 'media_org'))
        df['swe_media_country_mention'] = (df.url + df.country).apply(nice_string)
        return df

    def _identify_countries(self, dfs: list) -> pd.DataFrame:
        """
        Identify countries mentioned and drop articles without mentions.

        Parameters
        ----------
        dfs : list
            List of dataframes
        """
        # Merge dataframes
        for df in dfs:
            df.indexed = pd.to_datetime(df.indexed, utc=True)
        df = pd.concat(dfs, sort=True)

        # Drop unwanted rows and columns
        drop_cols = ['country', 'image', 'language', 'links', 'reference']
        df = df.drop(drop_cols, axis=1)
        dropper = ArticleDropper(drop_duplicates=False)
        df = dropper.transform(df)

        # Identify countries mentioned
        df['countries'] = identify_countries(df.headline + ' ' + df.lead)
        df.countries = df.countries.apply(lambda x: ','.join(set(x)))
        df = df[(df.countries.notnull()) & (df.countries != '')]

        return df

    def _count_countries(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Count number of media mentions in df by country and day.
        """
        df = df[['indexed', 'countries']]
        df = stretch(df, index_col='indexed', value_col='countries', sep=',')
        df['day'] = df.indexed.dt.strftime('%Y%m%d')
        df = df.groupby(['countries', 'day']).size()
        df = df.to_frame().reset_index()
        df.columns = ['country', 'day', 'swe_media_mentions']
        df = df.sort_values(['country', 'day'])
        return df

    def _check_latest_raw_ts(self) -> pd.Timestamp:
        """
        Check timestamp of newest article on S3.
        """
        files = list(self.datastore.list_files_in_folder('', suffix='csv'))
        latest_file = sorted(files)[-1]
        df = self.datastore.read_csv(latest_file)
        return pd.to_datetime(df.indexed, utc=True).max()

    def _sync_data_store(self) -> None:
        """
        Update S3 storage with all articles older than 24 hours.
        """
        ts = self._check_latest_raw_ts()
        delta = ts.utcnow() - ts
        if delta.days == 0:
            return
        fetcher = NewsFetcher()
        data = fetcher.fetch_period(ts.to_pydatetime(), pd.Timestamp.utcnow())
        df = pd.DataFrame(data)
        df.indexed = pd.to_datetime(df.indexed)
        df['month_year'] = (df.indexed.dt.year.astype(str)
                            .str.cat(df.indexed.dt.month.astype(str).str.zfill(2), '-'))
        for month_year in df.month_year.unique():
            key = f'mynewsflash/{month_year}.csv'
            if self.datastore.obj_exists(key):
                old = self.datastore.read_csv(key)
                old.indexed = pd.to_datetime(old.indexed)
                new = pd.concat([old, df[df.month_year == month_year]], sort=True)
            else:
                new = df[df.month_year == month_year]
            new = new.drop_duplicates(subset=['url'])
            new = new.sort_values('indexed')
            new = new.drop('month_year', axis=1)
            self.datastore.write_csv(new, key)
        return

    def save(self,
             path: Union[Path, str],
             recursive_concepts: bool = True,
             **kwargs: Any) -> None:

        log.info('Creating datapackage')

        kwargs.update({
            'author': 'Datastory',
            'default_measure': 'swe_media_mentions',
            'default_primary_key': ['country', 'day'],
            'name': 'mynewsflash',
            'source': 'MyNewsFlash',
            'status': 'draft',
            'title': 'MyNewsFlash',
            'topics': ['media', 'sweden'],
        })

        packages = list()
        for i, data in enumerate(self.data):
            package = DataPackage(data['data'])
            if data['datapoints']:
                package.set_datapoints(*data['datapoints'])
            packages.append(package)
        merge_packages(packages, path, **kwargs)

        log.info('Datapackage successfully created')
