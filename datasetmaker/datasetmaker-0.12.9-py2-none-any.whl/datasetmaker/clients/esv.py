import io
from typing import Union, Any
from pathlib import Path
import pandas as pd
from datasetmaker.models import Client
from datasetmaker.utils import get_remote_zip
from datasetmaker.datapackage import DataPackage
from datasetmaker.onto.manager import sid_to_id


class ESVClient(Client):
    url = ('https://www.esv.se/psidata/arsutfall/GetFile/?documentType=Utgift'
           '&fileType=Zip&fileName=%C3%85rsutfall%20utgifter%202006%20-%202018'
           ',%20definitivt.zip&year=2018&month=0&status=Definitiv')
    fname = 'Årsutfall utgifter 2006 - 2018, definitivt.csv'

    def get(self, **kwargs: Any) -> pd.DataFrame:
        zip_dict = get_remote_zip(self.url)
        bytes_ = zip_dict[self.fname]
        df = pd.read_csv(io.StringIO(bytes_.decode('utf8')),
                         sep=';',
                         decimal=',',
                         dtype={'Utgiftsområde': str,
                                'Utgiftsområde utfallsår': str,
                                'Anslag utfallsår': str,
                                'Anslag': str})
        df = df.pipe(self._clean)
        self.data = df
        return df

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        money_cols = ['Statens budget',
                      'Utfall',
                      'Ingående överföringsbelopp',
                      'Ändringsbudgetar',
                      'Indragningar',
                      'Utnyttjad del av medgivet överskridande',
                      'Anslagskredit',
                      'Utgående överföringsbelopp']

        for money_col in money_cols:
            df[money_col] = (
                df[money_col] * 1_000_000).round(0).astype('Int64')

        df['Anslag'] = df['Anslag'].str.replace(' ', '_').str.strip()

        df = df.drop(['Utgiftsområdesnamn utfallsår', 'Anslagsnamn utfallsår',
                      'Utgiftsområde utfallsår', 'Anslag utfallsår'], axis=1)

        df = df[df.Utgiftsområde.notnull()]

        df = df.rename(columns={
            'År': 'year',
            'Utgiftsområdesnamn': 'esv_expenditure__name',
            'Anslagsnamn': 'esv_allocation__name'})
        df = df.rename(columns=sid_to_id(source='esv'))

        return df

    def save(self, path: Union[Path, str], **kwargs: Any) -> None:
        measures = ['esv_ingoing_transfer_amount', 'esv_budget',
                    'esv_update_budgets', 'esv_retractions', 'esv_exceed',
                    'esv_outcome', 'esv_allocation_credit',
                    'esv_outgoing_transfer_amount']
        keys = ['esv_allocation', 'esv_expenditure', 'year']

        self.data.ddf.register_entity('esv_allocation')
        self.data.ddf.register_entity('esv_expenditure')

        for measure in measures:
            self.data.ddf.register_datapoints(measures=measure, keys=keys)

        package = DataPackage(data=self.data)

        kwargs.update({
            'author': 'Datastory',
            'default_measure': 'esv_budget',
            'default_primary_key': ['esv_allocation', 'esv_expenditure', 'year'],
            'name': 'ekonomistyrningsverket',
            'source': 'Ekonomistyrningsverket',
            'status': 'draft',
            'title': 'Ekonomistyrningsverket',
            'topics': ['economy', 'sweden'],
        })

        package.save(path)
