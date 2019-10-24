import pandas as pd
from datasetmaker.onto.manager import read_entity, read_synonyms

pd.options.mode.chained_assignment = None


def map_all(x: str, mapping: dict) -> list:
    return [mapping[i] for i in x]


def identify_countries(series: pd.Series) -> pd.Series:
    """Identifies countries mentioned in series.

    Parameters
    ----------
    series : pd.Series
        Series with text values.
    """
    def remove_hyphens(ser: pd.Series) -> pd.Series:
        return ser.str.replace('-', '').str.replace('–', '')

    def escape_chars(ser: pd.Series) -> pd.Series:
        return ser.str.replace('.', r'\.').str.replace('(', r'\(').str.replace(')', r'\)')

    series = series.pipe(remove_hyphens).str.lower()

    countries = read_entity('country', lang='sv-SE').query('country != "swe"')
    synonyms = read_synonyms('country', lang='sv-SE').query('country != "swe"')
    denonyms = synonyms[synonyms.synonym_type == 'denonym']
    alt_names = synonyms[synonyms.synonym_type == 'name']

    pat_name = countries.name.pipe(escape_chars).str.lower()
    pat_name = pat_name.pipe(remove_hyphens)
    pat_name = r'(\b' + r'|\b'.join(pat_name) + r'\b)s?\b'

    pat_alt = alt_names.synonym.pipe(escape_chars).str.lower()
    pat_alt = pat_alt.pipe(remove_hyphens)
    pat_alt = r'(\b' + r'|\b'.join(pat_alt) + r'\b)s?\b'

    pat_den = denonyms.synonym.pipe(escape_chars).str.lower()
    pat_den = pat_den.pipe(remove_hyphens)
    pat_den = r'(\b' + r'|\b'.join(pat_den) + r'\b)s?'

    name_map = countries[['name', 'country']].copy()
    name_map['name'] = name_map['name'].pipe(remove_hyphens).str.lower()
    name_map = name_map.set_index('name')
    name_map = name_map['country'].to_dict()

    denonym_map = denonyms.copy()
    denonym_map.synonym = denonym_map.synonym.pipe(remove_hyphens)
    denonym_map.synonym = denonym_map.synonym.str.lower()
    denonym_map = denonym_map.set_index('synonym')
    denonym_map = denonym_map['country'].to_dict()

    alt_map = alt_names.copy()
    alt_map.synonym = alt_map.synonym.pipe(remove_hyphens)
    alt_map.synonym = alt_map.synonym.str.lower()
    alt_map = alt_map.set_index('synonym')
    alt_map = alt_map['country'].to_dict()

    lookup = name_map
    lookup.update(denonym_map)
    lookup.update(alt_map)

    names_found = series.str.findall(pat_name)
    denonyms_found = series.str.findall(pat_den)
    alt_names_found = series.str.findall(pat_alt)
    found = names_found + denonyms_found + alt_names_found
    found = found.apply(map_all, args=(lookup,))
    return found.apply(sorted)
