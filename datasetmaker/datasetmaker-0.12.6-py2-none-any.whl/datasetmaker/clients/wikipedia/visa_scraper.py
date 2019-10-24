# flake8: noqa
# TODO: Fix linting errors of type E501

import io
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datasetmaker.onto.manager import _map


def fetch_visas() -> list:
    base_url = 'https://en.wikipedia.org'

    url_lists = ['w/index.php?title=Category:Visa_requirements_by_nationality',
                 ('w/index.php?title=Category:Visa_requirements_by_nationality'
                  '&pagefrom=Turkey%0AVisa+requirements+for+Turkish+citizens')]

    url_lists = [f'{base_url}/{url}' for url in url_lists]

    excluded = ['Visa_requirements_for_Abkhaz_citizens',
                'Visa_requirements_for_EFTA_nationals',
                'Visa_requirements_for_Estonian_non-citizens',
                'Visa_requirements_for_European_Union_citizens',
                'Visa_requirements_for_Latvian_non-citizens',
                'Visa_requirements_for_Artsakh_citizens',
                'Visa_requirements_for_Somaliland_citizens',
                'Visa_requirements_for_South_Ossetia_citizens',
                'Template:Timatic_Visa_Policy',
                'Visa_requirements_for_Transnistrian_citizens',
                'Template:Visa_policy_link']

    def get_country_links() -> list:
        links = []
        for url in url_lists:
            r = requests.get(url)
            html = BeautifulSoup(r.text, features='lxml')
            for link in html.select('.mw-category-group a')[:5]:
                href = f"{base_url}/{link.attrs['href'][1:]}"
                if href.split('/')[-1] not in excluded:
                    links.append(href)
        return links

    def get_country(url: str) -> tuple:
        title = url.split('/')[-1]
        return requests.get(url).text, title

    tables = [get_country(x) for x in get_country_links()]
    return tables


def scrape() -> pd.DataFrame:
    tables = fetch_visas()
    frames = []
    for table, title in tables:
        try:
            frame = pd.read_html(io.StringIO(table),
                                 match='Visa requirement',
                                 flavor='lxml')
            if len(frame) > 1:
                frame = [x for x in frame if 'Visa requirement' in x.columns][0]
            else:
                frame = frame[0]
            frame['Title'] = title
            frames.append(frame)
        except (ImportError, ValueError):
            continue

    def create_dataframe(tables: list) -> pd.DataFrame:
        clean_tables = []
        for t in tables:
            if type(t) is pd.DataFrame and t.shape[0] > 5:
                clean_tables.append(t)
        return pd.concat(clean_tables, sort=True)

    df = create_dataframe(frames)
    df = df.dropna(how='all', axis=1)
    df['Title'] = df['Title'].str.replace('Visa_requirements_for_', '')
    df = df.replace(r'\[[0-9]+\]', '', regex=True)
    df['Title'] = df['Title'].str.replace('%C3%A9', 'é')

    df['Title'] = (df['Title']
                   .str.replace('_', ' ')
                   .str.replace(' citizens', '')
                   .str.replace('citizens of North Macedonia', 'North Macedonia')
                   .str.replace('Chinese of ', '')
                   .replace('Democratic Republic of the Congo', 'Democratic Republic of Congo')
                   .replace('Republic of the Congo', 'Republic of Congo')
                   .replace('holders of passports issued by the ', '')
                   .str.strip())

    df = df[df.Title != 'British Nationals (Overseas)']
    df = df[df.Title != 'British Overseas']
    df = df[df.Title != 'British Overseas Territories']
    df = df[df.Title != 'holders of passports issued by the Sovereign Military Order of Malta']
    df = df[df['Title'] != 'crew members']

    if 'Notes' in df:
        df['Notes'] = df['Notes'].fillna(
            df['Notes (excluding departure fees)'])

    df = df.drop(['Notes (excluding departure fees)'], axis=1, errors='ignore')

    df['Visa requirement'] = (df['Visa requirement']
                              .str.lower()
                              .replace('evisa', 'electronic visa')
                              .replace('e-visa', 'electronic visa')
                              .replace('evisa required', 'electronic visa')
                              .replace('electronic visatr', 'electronic visa')
                              .str.replace('<', '', regex=False)
                              .str.replace(r'\[[Nn]ote 1\]', '')
                              .str.replace('[dubious – discuss]', '', regex=False)
                              .replace('electronic authorization system', 'electronic authorization')
                              .replace('electronic authorization', 'electronic authorisation')
                              .replace('electronic travel authorisation', 'electronic authorisation')
                              .replace('electronic travel authority', 'electronic authorisation')
                              .replace('electronic travel authorization', 'electronic travel authorisation')
                              .replace('visa not required (conditions apply)', 'visa not required (conditional)')
                              .replace('visa on arrival /evisa', 'visa on arrival / evisa')
                              .replace('visitor\'s permit on arrival', 'visitor permit on arrival')
                              .replace('visitor\'s permit is granted on arrival', 'visitor permit on arrival')
                              .replace('evisa/entri', 'evisa / entri')
                              .str.strip())

    df['_days'] = df['Allowed stay'].str.extract(
        '([0-9]+) ?q?day', flags=re.I)[0]
    df['_months'] = df['Allowed stay'].str.extract(
        '([0-9]+) mon?th', flags=re.I)[0]
    df['_weeks'] = df['Allowed stay'].str.extract(
        '([0-9]+) week', flags=re.I)[0]
    df['_years'] = df['Allowed stay'].str.extract(
        '([0-9]+) year', flags=re.I)[0]
    df['_fom'] = df['Allowed stay'].str.lower(
    ).str.extract('(freedom of movement)')[0]
    df['_unl'] = df['Allowed stay'].str.lower().str.extract('(unlimited)')[0]

    df['_days'] = (df['_days'].astype(float)
                   .fillna(df._weeks.astype(float) * 7)
                   .fillna(df._months.astype(float) * 30)
                   .fillna(df._years.astype(float) * 365)
                   .fillna(df._fom)
                   .fillna(df._unl))

    df = df.drop(['_months', '_weeks', '_years', '_fom', '_unl'], axis=1)
    df = df.rename(columns={'_days': 'Allowed stay days'})
    df = df.drop(['Allowed stay', 'Notes'], axis=1, errors='ignore')

    if 'Reciprocality' in df:
        df.wikipedia_visa_reciprocity = df.wikipedia_visa_reciprocity.fillna(
            df.Reciprocality)
        df = df.drop(['Reciprocality'], axis=1)

    if 'Reciprocity' not in df:
        df['Reciprocity'] = None
    else:
        df.Reciprocity = (df.Reciprocity
                            .replace('√', True)
                            .replace('Yes', True)
                            .replace('X', False)
                            .replace('✓', True))

    df = df.rename(columns={
        'Country': 'country_to',
        'Title': 'country_from',
        'Reciprocity': 'wikipedia_visa_reciprocity',
        'Visa requirement': 'visa_requirement',
        'Allowed stay days': 'visa_allowed_stay'
    })

    df = df.drop('wikipedia_visa_reciprocity', axis=1)

    df.visa_requirement = df.visa_requirement.str.replace('/', ' ')
    df.visa_requirement = df.visa_requirement.str.replace(r'\s+', '_')

    df.country_from = df.country_from.str.replace('excluding some Overseas territories', '')
    df.country_to = df.country_to.str.replace('excluding some Overseas territories', '')
    df.country_from = df.country_from.str.replace(' and territories', '')
    df.country_to = df.country_to.str.replace(' and territories', '')
    df.country_from = df.country_from.str.replace(' and external territories', '')
    df.country_to = df.country_to.str.replace(' and external territories', '')

    from_map = _map('country', 'name', 'country', synonym_types=['alt_name', 'denonym'])
    df['country_from'] = df['country_from'].map(from_map)
    df['country_to'] = df['country_to'].map(_map('country', 'name', 'country'))

    df = df.rename(columns={
        'country_from': 'country_flow.country_from',
        'country_to': 'country_flow.country_to'
    })

    df.ddf.register_entity('country', roles=['country_from', 'country_to'])
    df.ddf.register_entity('visa_requirement')
    df.ddf.register_datapoints(
        'visa_requirement', ['country_flow.country_from', 'country_flow.country_to'])

    return df
