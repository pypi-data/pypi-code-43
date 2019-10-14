import shutil
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from ddf_utils import package
from ddf_utils.io import dump_json

from datasetmaker.models import DataValidator
from datasetmaker.validate import validate_package
from datasetmaker.exceptions import EntityNotFoundException, MissingConceptError
from datasetmaker.utils import flatten
from datasetmaker.onto.schemas import schema_registry
from datasetmaker.onto.manager import (
    entity_exists,
    read_entity,
    read_concepts)


class DataPackage:
    """"
    Class for automatically creating data packages from data frames.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self.datapoints: list = []
        self.data = data
        self.concepts = self._create_concepts()
        self.entities = self._create_entities()

    def _create_concepts(self) -> pd.DataFrame:
        """
        Look up all concepts in the data, as well as any concepts
        that canonical entities in data reference.
        """
        concepts_list = list()
        cols = pd.Series(self.data.columns).str.split('.', expand=True)
        cols = pd.concat([cols[i] for i in range(cols.shape[1])]
                         ).dropna().drop_duplicates()
        initial_concepts = read_concepts(*cols)
        for concept in initial_concepts.concept:
            concepts_list.append(concept)
            schema = schema_registry.get(concept)
            if schema:
                concepts_list.extend(list(schema.keys()))
        concepts = read_concepts(*set(concepts_list))
        for concept in concepts.concept:
            schema = schema_registry.get(concept)
            if schema:
                concepts_list.extend(list(schema.keys()))
        concepts = read_concepts(*set(concepts_list))
        for i, composite in concepts[concepts.concept_type == 'composite'].iterrows():
            composite_domains = (composite.domain
                                 .replace('[', '')
                                 .replace(']', '')
                                 .replace(r'\s', '')
                                 .split(','))
            for domain in composite_domains:
                row = concepts.loc[concepts.concept == domain, :]
                concepts = concepts.append(row)
        concepts = concepts.drop_duplicates(subset=['concept'])

        for col in concepts.columns:
            if col not in concepts.concept.to_list():
                if col in ['concept', 'concept_type']:
                    continue
                concepts = concepts.append(
                    {'concept': col, 'concept_type': 'string'}, ignore_index=True)
        return concepts

    def _get_entity_props(self, cid: str) -> list:
        schema = schema_registry.get(cid)
        if not schema:
            raise EntityNotFoundException(cid)
        return list(schema.keys())

    def _assert_entity_is_valid(self, df: pd.DataFrame, schema: dict) -> None:
        """
        Raises if df does not conform to schema.
        """
        df = df.replace({np.nan: None})  # Cerberus does not understand nan
        v = DataValidator(schema)
        data = df.to_dict(orient='records')
        if not all(v.validate(x) for x in data):
            raise ValueError(v.errors)

    def _create_domain(self, cid: str) -> pd.DataFrame:
        props = self._get_entity_props(cid).copy()
        if cid in self.data:
            prop_cols = [x for x in self.data.columns if x.startswith(f'{cid}__')]
            data = self.data.filter(items=props + prop_cols).dropna(
                subset=[cid]).drop_duplicates(subset=[cid])
            data.columns = [x.split('__')[-1] for x in data.columns]
            if entity_exists(cid):
                data = data[[cid]].merge(read_entity(cid), on=cid, how='left')
            return data
        elif cid in flatten(self.data.columns.str.split('.')):
            roles = []
            props.remove(cid)
            role_cols = [x for x in self.data.columns if x.endswith(f'.{cid}')]
            for col in role_cols:
                data = self.data.filter(
                    items=[col] + [x for x in self.data.columns if col in x and x != col])
                data.columns = [x.split('.')[-1].split('__')[-1]
                                for x in data.columns]
                roles.append(data)
            data = pd.concat(roles, sort=True).dropna(
                subset=[cid]).drop_duplicates(subset=[cid])
            if entity_exists(cid):
                data = data.merge(read_entity(cid), on=cid, how='left')
            return data
        else:
            return read_entity(cid)

    def _create_entities(self) -> dict:
        entities = {}
        for _, concept in self.concepts.iterrows():
            if concept.concept_type == 'entity_domain':
                entities[concept.concept] = self._create_domain(
                    concept.concept)
            elif concept.concept_type == 'role':
                entities[concept.domain] = self._create_domain(
                    concept.domain)
        for cid, frame in entities.items():
            self._assert_entity_is_valid(frame, schema_registry.get(cid))
        return entities

    def set_datapoints(self, measures: list, keys: list) -> None:
        self.datapoints.append((measures, keys))

    def _cast_boolean_cols(self, df: pd.DataFrame) -> pd.DataFrame:
        booleans = df.select_dtypes('bool').columns
        for boolean in booleans:
            df[boolean] = df[boolean].astype(str).str.lower()
        return df

    def save(self, path: Union[Path, str], **kwargs: str) -> None:
        """
        Save the data as a DDF data package.
        """
        files = dict()

        path = Path(path)
        if path.exists():
            shutil.rmtree(path)
        path.mkdir()

        for name, frame in self.entities.items():
            frame = frame.pipe(self._cast_boolean_cols)
            files[f'ddf--entities--{name}.csv'] = frame

        for measures, keys in self.datapoints:
            measures_str = '--'.join(measures)
            keys_str = '--'.join(keys)
            fname = f'ddf--datapoints--{measures_str}--by--{keys_str}.csv'
            frame = (self.data[measures + keys]
                     .drop_duplicates()
                     .dropna()
                     .pipe(self._cast_boolean_cols))
            files[fname] = frame

        concepts = self.concepts.concept.to_list()
        for fname, frame in files.items():
            for col in frame.columns:
                for sub in col.split('.'):
                    if sub not in concepts:
                        raise MissingConceptError(f'{sub} not in concepts')
            frame.to_csv(path / fname, index=False)

        self.concepts.pipe(self._cast_boolean_cols).to_csv(path / 'ddf--concepts.csv', index=False)
        validate_package(path)
        self._ddfify(path, **kwargs)

    def _ddfify(self, path: Path, **kwargs: Union[str, list]) -> None:
        """
        Read the contents of a DDF package and create a datapackage.json file.
        """
        kwargs['status'] = kwargs.get('status', 'draft')
        kwargs['title'] = kwargs.get('title', kwargs.get('name', ''))
        kwargs['topics'] = kwargs.get('topics', [])
        kwargs['default_measure'] = kwargs.get('default_measure', '')
        kwargs['default_primary_key'] = '--'.join(
            sorted(kwargs.get('default_primary_key', [])))
        kwargs['author'] = kwargs.get('author', 'Datastory')
        meta = package.create_datapackage(path, **kwargs)
        dump_json(path / 'datapackage.json', meta)
