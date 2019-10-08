import numpy as np
import pandas as pd

from duodata.algemeen import generieke_kolomnamen

examenkandidaten_geslaagden_vo_url = 'https://duodata.nl/open_onderwijsdata/images/06-examenkandidaten-en-geslaagden-2013-2018.csv'
examenkandidaten_geslaagden_vo_url = 'https://duodata.nl/open_onderwijsdata/images/06-examenkandidaten-en-geslaagden-2013-2018.csv'


def _examenkandidaten_geslaagden_vo_ruw(examenkandidaten_geslaagden_vo_url=examenkandidaten_geslaagden_vo_url):
    """Download csv-bestand met gegevens over examenkandidaten vo van duodata"""
    data = pd.read_csv(examenkandidaten_geslaagden_vo_url, sep=";", encoding="latin1")
    return data


def _select_columns_examenkandidaten_geslaagden_vo():
    """Verwijder slaagpercentages (dat is tenslotte het resultaat van delen van gediplomeerden door examenkandidaten.
    Ook de TOTAAL-kolommen wordem verwijderd. Dat is tenslotte het resultaat van een sommering van de gegevens.
    Ook de ONBEKENDEN worden verwijderd, die zijn er niet of nauwelijks en leiden alleen maar af."""

    # lees data in:
    data = _examenkandidaten_geslaagden_vo_ruw()
    # Maak een lijst met kolommen die we willen bewaren.
    target_cols = [col for col in data.keys().tolist() if ((('GESLAAGDEN' in col) or ('EXAMENKAND' in col) or ('-')
                                                            not in col) and ('TOTAAL' not in col) and ('ONBEKEND' not in col))]
    # Beperk de dataset tot de kolommen die we willen hebben.
    result = data[target_cols].copy()
    return result


def _examenkandidaten_en_gediplomeerden_vo_op_een_regel(data):
    """Zet Geslaagden en Examenkandidaten op een regel."""
    fields = ['BRIN NUMMER',
              'VESTIGINGSNUMMER',
              'INSTELLINGSNAAM VESTIGING',
              'GEMEENTENAAM',
              'ONDERWIJSTYPE VO',
              'INSPECTIECODE',
              'OPLEIDINGSNAAM',
              'Geslacht',
              'Diplomajaar']

    # maak een set met geslaagden
    geslaagden = data[data.Gediplomeerden.notnull()].copy()
    del geslaagden['Examenkandidaten']

    # maak een set met examenkandidaten
    ex_kandidaten = data[data.Examenkandidaten.notnull()].copy()
    del ex_kandidaten['Gediplomeerden']

    # voeg ze samen
    result = pd.merge(ex_kandidaten, geslaagden, left_on=fields, right_on=fields, how='outer')

    return result


def examenkandidaten_gediplomeerden_vo():
    """Tabel met Gediplomeerden en Examenkandidaten per Brin, Vestiging, Onderwijstype
    en Gemeente.
    """
    data = _select_columns_examenkandidaten_geslaagden_vo()
    result = pd.melt(data, id_vars=['BRIN NUMMER', 'VESTIGINGSNUMMER', 'INSTELLINGSNAAM VESTIGING',
                                    'GEMEENTENAAM', 'ONDERWIJSTYPE VO', 'INSPECTIECODE', 'OPLEIDINGSNAAM'], value_name='Aantal')

    result['Geslacht'] = np.where(result.variable.str.contains('MAN'), 'Man', np.nan)
    result['Geslacht'] = np.where(result.variable.str.contains('VROUW'), 'Vrouw', result['Geslacht'])
    assert result.Geslacht.isnull().sum() == 0

    result['Examenkandidaten'] = np.where(result.variable.str.contains('EXAMENKANDIDATEN '), result.Aantal, np.nan)
    result['Examenkandidaten'] = pd.to_numeric(result.Examenkandidaten)
    result['Gediplomeerden'] = np.where(result.variable.str.contains('GESLAAGDEN '), result.Aantal, np.nan)
    result['Gediplomeerden'] = pd.to_numeric(result.Gediplomeerden)

    # maak een tussentabel aan waarbij het eerste jaar wordt afgesplitst:
    jaren = result.variable.str.split('-', expand=True)
    jaren['Diplomajaar'] = jaren[0].str[-4:]
    # voeg het eerste jaar toe aan de resultaattabel:
    result['Diplomajaar'] = jaren.Diplomajaar
    assert result.Diplomajaar.isnull().sum() == 0

    # verwijder de kolommen die we niet meer nodig hebben:
    del result['variable']
    del result['Aantal']

    tidy = _examenkandidaten_en_gediplomeerden_vo_op_een_regel(result)

    tidy = tidy[tidy.Examenkandidaten > 0].copy()

    tidy.Diplomajaar = tidy.Diplomajaar.astype(int)
    tidy = tidy.rename(columns=generieke_kolomnamen)
    return tidy


def _schoolnamen_vo():
    """Tabel per brin-nummer, naam instelling en plaatsnaam. Er wordt gekozen voor de meest recente naam (basis van diplomajaar)."""
    fields = ['Brin', 'NaamInstelling', 'Gemeente']
    result = examenkandidaten_gediplomeerden_vo()
    result = result.sort_values(by=['Diplomajaar'], ascending=False).drop_duplicates(subset=['Brin'], keep='first')[fields]
    return result
