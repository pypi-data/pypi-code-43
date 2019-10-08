import pandas as pd

from duodata.algemeen import generieke_kolomnamen

gediplomeerden_mbo_url = ("https://duodata.nl/open_onderwijsdata/images/10.-gediplomeerden-"
                          "per-instelling%2C-plaats%2C-kenniscentrum%2C-sector%2C-sectorunit%2C-type-mbo"
                          "%2C-opleiding%2C-niveau%2C-geslacht.csv")

gediplomeerden_mbo_url = ("https://duodata.nl/open_onderwijsdata/images/"
                          "10-gediplomeerden-per-instelling-plaats-kenniscentrum-sector-bedrijfstak-type-"
                          "mbo-opleiding-niveau-geslacht-2014-2018.csv")


def _gediplomeerden_mbo_bestand(gediplomeerden_mbo_url=gediplomeerden_mbo_url):
    """Lees bestand in met mbo-gediplomeerden van duodata-site"""
    data = pd.read_csv(gediplomeerden_mbo_url, sep=';', encoding='latin1')
    return data


def gediplomeerden_mbo():
    """Maak de eerste data tabel in tidy format.
    De TOTAAL-kolommen worden verwijderd.
    De tabel wordt in tidy format gezet.
    Kolommen voor Geslacht, Diplomajaar en Gediplomeerden worden toevoegd.
    Diplomajaar wil zeggen dat studenten in het betreffende collegejaar het diploma hebben behaald.
    In het bronbestand worden kolommen gebruikt als DIPVRW2018. Het jaartal daarin wordt gebruikt als
    Diplomajaar. Echter, in het bestand dat op 1 oktober wordt gepubliceerd, bevat al de cijfers van
    collegejaar 2018. Dat kan natuurlijk niet. Bedoeld wordt het diplomajaar 2017 (zoals bevestigd door
    duodata in een mail 9 mei 2018).
    """
    gediplomeerden_ruw = _gediplomeerden_mbo_bestand()

    # Maak een lijst met kolommen, zonder TOTAAL:
    target_cols = [col for col in gediplomeerden_ruw.keys().tolist() if 'TOTAAL' not in col]
    # Maak een lijst met id_vars:
    id_vars = [col for col in target_cols if not col.startswith('DIP')]

    tidy = pd.melt(gediplomeerden_ruw[target_cols], id_vars=id_vars, var_name='Variabele', value_name='Gediplomeerden')

    # Maak een kolom Diplomajaar:
    tidy['Diplomajaar'] = tidy.Variabele.str[-4:]
    tidy['Diplomajaar'] = pd.to_numeric(tidy['Diplomajaar'], errors='coerce')
    tidy['Diplomajaar'] = tidy['Diplomajaar'] - 1
    # Maak een kolom geslacht:
    tidy['Geslacht'] = tidy.Variabele.str[-7:-4]
    tidy['Geslacht'] = tidy['Geslacht'].replace({'MAN': 'Man', 'VRW': 'Vrouw'})
    assert tidy['Geslacht'].nunique() == 2
    # Verwijder Variabele
    del tidy['Variabele']
    # Verwijder rijen waarbij Gediplomeerden leeg is of 0:
    tidy.dropna(subset=['Gediplomeerden'], inplace=True)

    result = tidy[tidy.Gediplomeerden != 0].copy()
    result.Diplomajaar = result.Diplomajaar.astype(int)
    # Geef kolommen  generieke namen:
    result = result.rename(columns=generieke_kolomnamen)
    return result


def _schoolnamen_mbo():
    """Tabel per brin-nummer, naam instelling en plaatsnaam. Er wordt gekozen voor de meest recente naam."""
    fields = ['Brin', 'NaamInstelling', 'Plaats']
    result = gediplomeerden_mbo()
    result = result.sort_values(by=['Diplomajaar'], ascending=False).drop_duplicates(subset=['Brin'], keep='first')[fields]
    return result
