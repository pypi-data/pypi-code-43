import pandas as pd

from duodata.mbo.gediplomeerden import gediplomeerden_mbo, _schoolnamen_mbo
from duodata.vo.examenkandidaten import examenkandidaten_gediplomeerden_vo, _schoolnamen_vo


def mbo4_toestroom_per_jaar_brin():
    """MBO gediplomeerden per jaar per brin met kwalificatieniveau 4"""
    data = gediplomeerden_mbo()
    filter_mbo4 = data.Kwalificatieniveau == 4
    data['Instroomcohort'] = data.Diplomajaar + 1
    result = data[(filter_mbo4)].groupby(['Instroomcohort', 'Brin', ]).Gediplomeerden.sum().reset_index()
    result.Instroomcohort = result.Instroomcohort.astype(int)
    result['Vooropleiding'] = 'mbo'
    return result


def havo_vwo_toestroom_per_jaar_brin():
    data = examenkandidaten_gediplomeerden_vo()
    data['Instroomcohort'] = data.Diplomajaar + 1
    data['Vooropleiding'] = data['Onderwijstype'].replace({'HAVO': 'havo', 'VWO': 'vwo'})
    filter_havo_vwo = data.Onderwijstype.isin(['HAVO', 'VWO'])

    result = data[(filter_havo_vwo)].groupby(['Instroomcohort', 'Brin', 'Vooropleiding']).Gediplomeerden.sum().reset_index()
    result.Instroomcohort = result.Instroomcohort.astype(int)

    return result


def toestroom_hbo():
    """Potentiele hbo-toestroom uit mbo, havo en vwo, per jaar en brin."""
    # Lees alle mbo in:
    mbo4_per_jaar_brin = mbo4_toestroom_per_jaar_brin()
    # Lees alle havo en vwo
    havo_vwo_gediplomeerden_per_jaar_brin = havo_vwo_toestroom_per_jaar_brin()
    # voeg ze samen
    result = pd.concat([mbo4_per_jaar_brin, havo_vwo_gediplomeerden_per_jaar_brin], sort=False)

    assert mbo4_per_jaar_brin.Instroomcohort.max() == havo_vwo_gediplomeerden_per_jaar_brin.Instroomcohort.max()
    return result


def schoolnamen_mbo_vo():
    """Een dataset met unieke brins. Per brin een schoolnaam en gemeente. De brins van mbo en vo zijn samengevoegd
    zodat er een tabel ontstaat met brin als sleutel. Er is hierbij
    flink ontdubbeld, dat betekent met name dat de plaatsnamen soms niet kloppen, soms wisselen
    besturen van vestigingsplaats. Er is alsvolgt ontdubbeld: mbo en vo zijn de gegevens van het meest recente
    brin gebruikt (van het meest recente jaar).
    Daarna zijn mbo en vo samengevoegd en is nogmaals ontdubbeld. De gegevens van de vo zijn
    overgenomen, die van mbo vervallen."""

    vo_namen = _schoolnamen_vo()
    vo_namen['Type'] = 'vo'

    mbo_namen = _schoolnamen_mbo().rename(columns={'Plaats': 'Gemeente'})
    mbo_namen['Type'] = 'mbo'
    # Voeg samen:
    schoolnamen = pd.concat([vo_namen, mbo_namen], sort=False).sort_values(by=['Type'], ascending=False)
    # ontdubbel (laat mbo vallen)
    schoolnamen = schoolnamen.drop_duplicates(subset='Brin', keep='first')
    # verwijder hulpkolom
    del schoolnamen['Type']

    return schoolnamen
