import io
import calendar
import pandas as pd
import numpy as np
import requests
from datasetmaker.onto.manager import _map


base_url = "https://en.wikipedia.org/wiki"


def fetch_html() -> str:
    url = f'{base_url}/List_of_next_general_elections'
    return requests.get(url).text


def scrape() -> pd.DataFrame:
    html = fetch_html()
    tables = pd.read_html(io.StringIO(html), match="Parliamentary")
    df = pd.concat(tables, sort=True)

    cols = [
        "country",
        "wikipedia_fair",
        "wikipedia_power",
        "wikipedia_parl_prev",
        "wikipedia_parl_next",
        "wikipedia_parl_term",
        "wikipedia_pres_prev",
        "wikipedia_pres_next",
        "wikipedia_pres_term",
        "wikipedia_status",
    ]

    keep_cols = [
        "country",
        "wikipedia_parl_prev",
        "wikipedia_parl_next",
        "wikipedia_parl_term",
        "wikipedia_pres_prev",
        "wikipedia_pres_next",
        "wikipedia_pres_term",
    ]

    df.columns = cols
    df = df[keep_cols]

    # Remove countries with no next election info
    df = df[df.wikipedia_parl_next.notnull()]

    # Remove European Union
    df = df[df.country != 'European Union']

    # Convert previous election to datetime
    df["wikipedia_parl_prev"] = pd.to_datetime(df.wikipedia_parl_prev)

    # Remove footnotes
    try:
        df.wikipedia_parl_term = df.wikipedia_parl_term.str.split("[", expand=True)[0]
        df.wikipedia_pres_term = df.wikipedia_pres_term.str.split("[", expand=True)[0]
    except AttributeError:
        pass  # No footnotes present

    df.wikipedia_parl_next = parse_wikipedia_time(df.wikipedia_parl_next)
    df.wikipedia_pres_next = parse_wikipedia_time(df.wikipedia_pres_next)

    try:
        df.wikipedia_parl_term = df.wikipedia_parl_term.str.split(" ", expand=True)[0]
    except AttributeError:
        pass

    df.country = df.country.replace("Korea", "South Korea")
    df["iso_3"] = df.country.map(_map('country', 'name', 'country'))

    df = df.drop('country', axis=1).rename(columns={'iso_3': 'country'})
    df = df.dropna(subset=["country"])

    # Temp
    df = df[['wikipedia_parl_next', 'country']]
    df.columns = ['day', 'country']
    df['election'] = df.country.str.cat(df.day.astype(str), '_')
    df['type'] = 'parliamentary'

    df.ddf.register_entity('election', props=['country', 'day', 'type'])

    return df


def parse_wikipedia_time(ser: pd.Series) -> pd.Series:
    year = ser.str[-4:]
    month = ser.str.extract(r'(\D+)')[0]
    month = month.str.strip()
    day = ser.str.extract(r'(\d{1,2}) ')[0]

    month_names = list(calendar.month_name)

    month = month.apply(
        lambda x: str(month_names.index(x)).zfill(
            2) if x in month_names else np.nan
    )

    month = month.astype(str).str.replace("nan", "")
    day = day.astype(str).str.zfill(2).str.replace("nan", "")

    ser = year + '-' + month + '-' + day

    ser = ser.str.replace("-nan", "")
    ser = ser.str.replace('-+$', '', regex=True)
    return ser
