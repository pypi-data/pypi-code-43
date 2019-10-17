import pandas as pd


class ArticleDropper():
    """Removes articles that for one reason or another are not relevant to
    include for classification or country identification purposes.

    Parameters
    ----------

    drop_brands : boolean, True by default
        Drop sub brands such as traveling sections.
    drop_debate : boolean, True by default
        Drop debate articles.
    drop_duplicates : boolean, True by default
        Drop articles with duplicated headline or lead.
    drop_len : boolean, True by default
        Drop by text length as defined by maxl, minl, maxh and minh.
    drop_mixed : boolean, True by default
        Drop articles with mixed content, such as news summaries.
    dropna : boolean, True by default
        Drop articles with missing headline or lead.
    maxl : int
        Max length of lead
    minl : int
        Min length of lead.
    maxh : int
        Max length of headline
    minh : int
        Min length of headline
    """

    def __init__(self,
                 drop_brands: bool = True,
                 drop_debate: bool = True,
                 drop_duplicates: bool = True,
                 drop_len: bool = True,
                 drop_mixed: bool = True,
                 dropna: bool = True,
                 maxl: int = 400,
                 minl: int = 45,
                 maxh: int = 100,
                 minh: int = 10) -> None:
        self.drop_brands = drop_brands
        self.drop_debate = drop_debate
        self.drop_duplicates = drop_duplicates
        self.drop_len = drop_len
        self.drop_mixed = drop_mixed
        self.dropna = dropna
        self.maxl = maxl
        self.minl = minl
        self.maxh = maxh
        self.minh = minh

    def _drop_brands(self, df: pd.DataFrame) -> pd.DataFrame:
        brands = ['Allt om Resor', 'SvD Näringsliv']
        return df[~df.source.isin(brands)]

    def _drop_debate(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[~df.url.str.contains('svt.se/opinion/')]
        df = df[~df.url.str.contains('gp.se/nyheter/debatt/')]
        df = df[~df.url.str.contains('expressen.se/ledare/')]
        df = df[~df.lead.str.startswith('DEBATT')]
        df = df[~df.lead.str.startswith('ANALYS')]
        df = df[~df.lead.str.startswith('KOMMENTAR')]
        df = df[~df.lead.str.startswith('GÄST')]
        df = df[~df.lead.str.startswith('LEDARE')]
        df = df[~df.lead.str.startswith('KRÖNIKA')]
        df = df[~df.headline.str.startswith('LEDARE')]
        df = df[~df.headline.str.startswith('Ledare: ')]
        return df

    def _drop_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.drop_duplicates(subset=['headline'])
        df = df.drop_duplicates(subset=['lead'])
        return df

    def _drop_len(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[df.lead.str.len() <= self.maxl]
        df = df[df.lead.str.len() >= self.minl]
        df = df[df.headline.str.len() <= self.maxh]
        df = df[df.headline.str.len() >= self.minh]
        return df

    def _drop_mixed(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[~df.lead.str.contains('detta hände när du sov')]
        df = df[~df.url.str.contains('medan-du-sov')]
        df = df[~df.url.str.contains('/tv-tabla/')]
        df = df[~df.url.str.contains('programid=438')]  # godmorgon världen
        df = df[~df.url.str.contains('programid=185')]  # Sisuradio
        return df

    def _dropna(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna(subset=['headline', 'lead'])

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Execute all droppings on df."""
        if self.dropna:
            df = self._dropna(df)
        if self.drop_brands:
            df = self._drop_brands(df)
        if self.drop_debate:
            df = self._drop_debate(df)
        if self.drop_duplicates:
            df = self._drop_duplicates(df)
        if self.drop_len:
            df = self._drop_len(df)
        if self.drop_mixed:
            df = self._drop_mixed(df)

        return df
