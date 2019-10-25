import pandas as pd
from datasetmaker.onto.manager import _map


base_url = "https://en.wikipedia.org/wiki"


def scrape() -> pd.DataFrame:
    url = f'{base_url}/List_of_current_heads_of_state_and_government'
    tables = pd.read_html(url)
    df = pd.concat(tables[1:4], sort=True)
    df = df.drop('Also claimed by', axis=1)
    df['State'] = df['State'].fillna(df['State/Government'])
    df = df.drop('State/Government', axis=1)
    df.columns = ['head_gov', 'head_state', 'country']
    df['country'] = df.country.map(_map('country', 'name', 'country'))

    head_state = (df
                  .head_state
                  .str.replace(r'\xa0', ' ')
                  .str.split(r'\[α\]', expand=True)[0]
                  .str.split(r'\[δ\]', expand=True)[0]
                  .str.split(r'\[γ\]', expand=True)[0]
                  .str.split(r'\[κ\]', expand=True)[0]
                  .str.split(r'\[θ\]', expand=True)[0]
                  .str.split(r'\[ι\]', expand=True)[0]
                  .str.split(' – ', n=-1, expand=True)).copy()

    df['head_state'] = head_state[1].str.strip().str.replace(r'\s',
                                                             '_').str.lower()
    df['head_state__title'] = head_state[0].str.strip()
    df['head_state__name'] = head_state[1].str.strip()

    head_gov = (df
                .head_gov
                .str.replace(r'\xa0', ' ')
                .str.split(r'\[α\]', expand=True)[0]
                .str.split(r'\[δ\]', expand=True)[0]
                .str.split(r'\[γ\]', expand=True)[0]
                .str.split(r'\[κ\]', expand=True)[0]
                .str.split(r'\[θ\]', expand=True)[0]
                .str.split(r'\[ι\]', expand=True)[0]
                .str.split(' – ', n=-1, expand=True)).copy()

    df['head_gov'] = head_gov[1].str.strip().str.replace(r'\s', '_').str.lower()
    df['head_gov__title'] = head_gov[0].str.strip()
    df['head_gov__name'] = head_gov[1].str.strip()

    df = df.sort_values('country')
    df = df.reset_index(drop=True)

    df.ddf.register_entity('head_gov', props=['country'])
    df.ddf.register_entity('head_state', props=['country'])
    df.ddf.register_entity('country')

    return df
