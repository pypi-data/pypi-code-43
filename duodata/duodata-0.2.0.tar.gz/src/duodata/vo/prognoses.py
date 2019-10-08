import numpy as np
import pandas as pd

from duodata.algemeen import generieke_kolomnamen

eerste_prognose_jaar = 2018
prognoses_vo_url = "https://duodata.nl/open_onderwijsdata/images/11-leerlingenprognose-vo-2012-2037.csv"


def _prognoses_vo_bestand(prognoses_vo_url=prognoses_vo_url):
    """Lees bestand in met prognoses van duodata-site"""
    data = pd.read_csv(prognoses_vo_url, sep=';', encoding='latin1')
    return data


def prognoses_vo():
    """"Prognoses voor aantal studenten in voortgezet onderwijs."""
    data = _prognoses_vo_bestand()

    # Maak een lijst met namen van kolommen, zonder TOTAAL:
    # TOTAAL hebben we niet nodig want is de som van de overige aantallen.
    target_cols = [col for col in data.keys().tolist() if 'totaal' not in col]

    # alle variabelen die niet beginnen met een van de onderwijstypen
    # zijn id_variabelen.
    onderwijstypen = ['BRJ', 'VMBO', 'HAVO', 'VWO', 'PRO']
    id_vars = target_cols
    for onderwijstype in onderwijstypen:
        id_vars = [col for col in id_vars if not col.startswith(onderwijstype)]

    # zet om naar tidy format:
    tidy = pd.melt(data[target_cols], id_vars=id_vars, var_name='Variabele', value_name='Aantal')

    # Haal onderwijstype en studiejaar uit Variabele kolom:
    extra = tidy.Variabele.str.split('.', expand=True).rename(columns={0: 'Onderwijstype', 1: 'Studiejaar'})
    # Voeg kolommen toe:
    tidy['Onderwijstype'] = extra.Onderwijstype
    tidy['Studiejaar'] = extra.Studiejaar
    tidy['Studiejaar'] = tidy.Studiejaar.astype(int)
    tidy['Aantal'] = pd.to_numeric(tidy.Aantal, errors='coerce')

    # Sommige aantallen zijn prognoses, sommmige zijn reeel:
    tidy['TypeAantal'] = np.where(tidy.Studiejaar < eerste_prognose_jaar, 'ReëleAantal', 'Prognose')

    onderwijstype = {'BRJ': 'Brugjaar', }
    tidy['Onderwijstype'] = tidy['Onderwijstype'].replace(onderwijstype)
    result = tidy.rename(columns=generieke_kolomnamen)
    return result
