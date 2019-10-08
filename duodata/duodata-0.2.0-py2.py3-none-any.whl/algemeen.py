import googlemaps
from datetime import datetime
from duodata.settings import google_api_key

generieke_kolomnamen = {'BRIN NUMMER': "Brin",
                        'VESTIGINGSNUMMER': "Brinvolgnummer",
                        'INSTELLINGSNAAM VESTIGING': "NaamInstelling",
                        'GEMEENTENAAM': 'Gemeente',
                        'ONDERWIJSTYPE VO': "Onderwijstype",
                        'INSPECTIECODE': 'CodeInspectie',
                        'OPLEIDINGSNAAM': 'NaamOpleiding',
                        'onderwijssoort': 'Onderwijssoort',
                        'BRIN': 'Brin',
                        'brin_naam': 'NaamInstelling',
                        'brin_adres': 'Adres',
                        'brin_pc': 'Postcode',
                        'brin_plaats': 'Plaats',
                        'brin_provincie': 'Provincie',
                        'brin_gemnr': 'Gemeentenummer',
                        'brin_gemeente': 'Gemeente',
                        'bgnummer': 'BevoegdGezag',
                        'bg_naam': 'NaamBevoegdGezag',
                        'bg_adres': 'AdresBevoegdGezag',
                        'bg_pc': "PostcodeBevoegdGezag",
                        'bg_plaats': "PlaatsBevoegdGezag",
                        'bg_provincie': "ProvincieBevoegdGezag",
                        'bg_gemnr': 'GemeenteNummerBevoegdGezag',
                        'bg_gemeente': 'GemeenteBevoegdGezag',
                        'INSTELLINGSNAAM': "NaamInstelling",
                        'PLAATSNAAM': "Plaats",
                        'TYPE MBO': "TypeMBO",
                        'KWALIFICATIENIVEAU': "Kwalificatieniveau",
                        'KWALIFICATIE CODE': "Kwalificatiecode",
                        'KWALIFICATIE NAAM': "Kwalificatienaam",
                        'MBO SECTOR': "MBOsector",
                        'DOMEIN': "Domein",
                        'SECTORUNIT SBB': "SectorUnitSBB",
                        'BRIN NUMMER KENNISCENTRUM': "BrinKenniscentrum",
                        'NAAM KENNISCENTRUM': "NaamKenniscentrum",
                        'GEMEENTENAAM VESTIGING': 'GemeenteVestiging',
                        'PROVINCIE VESTIGING': 'ProvincieVestiging',
                        'LEERWEG VMBO': 'LeerwegVMBO',
                        'VMBO SECTOR': 'VMBOsector',
                        'AFDELING': 'Afdeling',
                        'EXAMENKANDIDATEN': 'Examenkandidaten',
                        'GESLAAGDEN': 'Geslaagden',
                        'GEZAKTEN': 'Gezakten',
                        'GEMIDDELD CIJFER SCHOOLEXAMEN': 'GemiddeldCijferSchoolexamen',
                        'GEMIDDELD CIJFER CENTRAAL EXAMEN': 'GemiddeldCijferCentraalExamen',
                        'GEMIDDELD CIJFER CIJFERLIJST': 'GemiddeldCijferCijferlijst'
                        }


def get_distance_to_hsl(series, destination='Hogeschool Leiden, Leiden', google_api_key=google_api_key):
    """Haalt reisafstand en reistijd op bij Google."""
    result = series
    gmaps = googlemaps.Client(key=google_api_key)

    try:
        googleresult = gmaps.distance_matrix(origins=series.NaamInstelling + ', ' + series.Gemeente,
                                             destinations=destination,
                                             mode='transit',
                                             language='nl',
                                             units='metrics',
                                             arrival_time=datetime(2019, 5, 9, 8, 30, 0)
                                             )
        result['StatusGoogleAfstand'] = googleresult['status']
        result['test'] = 'test'
        result['OvAfstandMeter'] = googleresult['rows'][0]['elements'][0]['distance']['value']
        result['OvAfstand'] = googleresult['rows'][0]['elements'][0]['distance']['text']
        result['OvReistijdSeconden'] = googleresult['rows'][0]['elements'][0]['duration']['value']
        result['OvReistijd'] = googleresult['rows'][0]['elements'][0]['duration']['text']
    except Exception:
        try:
            googleresult = gmaps.distance_matrix(origins=series.Gemeente,
                                                 destinations='Hogeschool Leiden, Leiden',
                                                 mode='transit',
                                                 language='nl',
                                                 units='metrics',
                                                 arrival_time=datetime(2019, 5, 9, 8, 30, 0)
                                                 )
            result['StatusGoogleAfstand'] = googleresult['status']
            result['test'] = 'test'
            result['OvAfstandMeter'] = googleresult['rows'][0]['elements'][0]['distance']['value']
            result['OvAfstand'] = googleresult['rows'][0]['elements'][0]['distance']['text']
            result['OvReistijdSeconden'] = googleresult['rows'][0]['elements'][0]['duration']['value']
            result['OvReistijd'] = googleresult['rows'][0]['elements'][0]['duration']['text']
        except Exception:
            result['StatusGoogleAfstand'] = 'Er ging iets mis'
    finally:
        return result
