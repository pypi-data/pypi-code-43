from typing import Dict, Union, Optional, Iterator
from pathlib import Path
from functools import lru_cache
from collections.abc import MutableMapping
import pandas as pd
import ddf_utils
from datasetmaker.path import DDF_DIR
from datasetmaker.exceptions import EntityNotFoundException
from datasetmaker.utils import CSV_DTYPES


@lru_cache()
def read_concepts(*subset: str, recursive: bool = True) -> pd.DataFrame:
    """
    Reads the ontology concepts CSV file.

    Parameters
    ----------
    subset
        Concepts to include (optional)
    """
    path = DDF_DIR / f'ddf--concepts.csv'
    concepts = pd.read_csv(path, sep=',', dtype=CSV_DTYPES)
    concepts = concepts.drop('context', axis=1, errors='ignore')
    if not subset:
        return concepts
    df = concepts[concepts.concept.isin(subset)]

    if not recursive:
        return df

    for i, role in df[df.concept_type == 'role'].copy().iterrows():
        if role.domain not in df.concept:
            df = df.append(concepts[concepts.concept == role.domain])
    return df.drop_duplicates()


# @lru_cache()
def read_entity(name: str, lang: Optional[str] = None) -> pd.DataFrame:
    """
    Reads an entity CSV file and returns a dataframe.

    Parameters
    ----------
    name
        Name of entity.
    lang
        Language.
    """
    if lang:
        path = DDF_DIR / f'lang/{lang}' / f'ddf--entities--{name}.csv'
    else:
        path = DDF_DIR / f'ddf--entities--{name}.csv'
    return pd.read_csv(path, sep=',', dtype=CSV_DTYPES)


@lru_cache()
def read_synonyms(name: str, lang: Optional[str] = None) -> pd.DataFrame:
    """
    Reads a synonyms file for an entity and returns a dataframe.

    Parameters
    ----------
    name
        Name of entity.
    lang
        Language.
    """
    if lang:
        path = DDF_DIR / f'lang/{lang}' / f'ddf--synonyms--{name}.csv'
    else:
        path = DDF_DIR / f'ddf--synonyms--{name}.csv'
    return pd.read_csv(path, sep=',', dtype=CSV_DTYPES)


def entity_exists(name: str, lang: Optional[str] = None) -> bool:
    """
    Entity `name` exists in ontology.

    Parameters
    ----------
    name
        Name of entity.
    lang
        Language.
    """
    if lang:
        path = DDF_DIR / f'lang/{lang}' / f'ddf--entities--{name}.csv'
    else:
        path = DDF_DIR / f'ddf--entities--{name}.csv'
    return path.exists()


def synonyms_exist(name: str, lang: Optional[str] = None) -> bool:
    """
    Synonyms `name` exists in ontology.

    Parameters
    ----------
    name
        Synonyms name.
    lang
        Language.
    """
    if lang:
        path = DDF_DIR / f'lang/{lang}' / f'ddf--synonyms--{name}.csv'
    else:
        path = DDF_DIR / f'ddf--synonyms--{name}.csv'
    return path.exists()


def sid_to_id(source: str) -> dict:
    """
    Map from source identifiers to internal identifiers.

    Parameters
    ----------
    source
        Data source.
    """
    df = read_concepts().query(
        f'(source == "{source}") | (source.isnull())')
    df.sid = df.sid.fillna(df.concept)
    return df.set_index('sid').concept.to_dict()


def id_to_sid(source: str) -> dict:
    """
    Map from internal identifiers to source identifiers.

    Parameters
    ----------
    source
        Data source.
    """
    df = read_concepts().query(f'source == "{source}"')
    return df.set_index('concept').sid.to_dict()


def id_to_name(source: str) -> dict:
    """
    Map from internal identifiers to names.

    Parameters
    ----------
    source
        Data source.

    Examples
    --------
    >>> mapping = id_to_name(source='scb')
    >>> mapping.get('scb_psu_party_sympathy')
    'PSU party sympathy'
    """
    df = read_concepts().query(f'source == "{source}"')
    return df.set_index('concept').name.to_dict()


def _map(entity_name: str,
         key: str,
         value: str,
         include_synonyms: bool = True,
         synonym_types: list = ['name']) -> MutableMapping:
    """
    Create a mapping from one or multiple fields of the given
    entity to the value field.

    Parameters
    ----------
    entity_name : str, name of entity
    key : str, entity field to map from
    value : str, entity field to map to
    include_synonyms : bool, whether to include synonyms
    synonym_types : list, subset of synonyms to include
    """
    df = read_entity(entity_name)
    map_: Dict[str, str] = dict()

    frame = df[[key] + [value]].dropna()
    map_.update(frame.set_index(key)[value].to_dict())
    if include_synonyms and synonyms_exist(entity_name):
        synonyms = read_synonyms(entity_name)
        synonyms = synonyms[synonyms.synonym_type.isin(synonym_types)]
        map_.update(synonyms.set_index('synonym')[value].to_dict())
    return EntityDict(entity_name, map_)


def add_entity_to_package(package_path: Union[Path, str],
                          entity_name: str) -> None:
    """
    Convenience function to add ad hoc entities to existing packages

    Parameters
    ----------
    package_path : str or pathlib.Path, path to existing data package.
    entity_name : str, name of entity in question.
    """

    package_path = Path(package_path)
    package_concepts_path = package_path / 'ddf--concepts.csv'
    package_concepts = pd.read_csv(package_concepts_path, dtype=CSV_DTYPES)
    if package_concepts.concept.str.contains(entity_name).any():
        return
    ontology_concepts = read_concepts()
    ontology_concept = ontology_concepts.loc[
        ontology_concepts.concept == entity_name]
    if ontology_concept.empty:
        raise ValueError('Entity does not exist in ontology')
    package_concepts = package_concepts.append(ontology_concept, sort=True)
    package_concepts.to_csv(package_concepts_path, index=False)
    entity_path = DDF_DIR / f'ddf--entities--{entity_name}.csv'
    entity_frame = pd.read_csv(entity_path, sep=',', dtype=CSV_DTYPES)
    entity_frame.to_csv(package_path / f'ddf--entities--{entity_name}.csv',
                        index=False)
    meta = ddf_utils.package.create_datapackage(package_path)
    ddf_utils.io.dump_json(package_path, 'datapackage.json', meta)


class EntityDict(MutableMapping):
    def __init__(self, entity_name: str, data: dict = {}):
        self.entity_name = entity_name
        self.mapping: dict = {}
        self.update({k.lower(): v for k, v in data.items()})

    def __getitem__(self, key: str) -> Optional[str]:
        if type(key) is float:  # NaN
            return None
        if not key.lower() in self.mapping:
            self.__missing__(key)
        return self.mapping[key.lower()]

    def __delitem__(self, key: str) -> None:
        del self.mapping[key.lower()]

    def __setitem__(self, key: str, value: str) -> None:
        self.mapping[key.lower()] = value

    def __missing__(self, key: str) -> None:
        raise EntityNotFoundException(
            f'Instance "{key}" of entity "{self.entity_name}" not found')

    def __call__(self, key: str) -> Optional[str]:
        return self.__getitem__(key)

    def __iter__(self) -> Iterator:
        return iter(self.mapping)

    def __len__(self) -> int:
        return len(self.mapping)

    def __repr__(self) -> str:
        return str(self.mapping)
