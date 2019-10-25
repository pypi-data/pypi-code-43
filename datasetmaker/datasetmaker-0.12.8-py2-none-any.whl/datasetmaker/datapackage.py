import shutil
import logging
from pathlib import Path
from typing import Union, Dict

import pandas as pd
from ddf_utils import package
from ddf_utils.io import dump_json

from datasetmaker.validate import validate_package
from datasetmaker.onto.manager import (
    entity_exists,
    read_entity,
    read_concepts)

log = logging.getLogger(__name__)


class DataPackage:
    """
    Class for automatically creating data packages from data frames.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self.datapoints: dict = dict()
        self.data = data

        concepts = self._create_concepts(data)
        concepts = self._hydrate_concepts(concepts)
        self.concepts = concepts

        self.entities = self._create_entities()
        self.datapoints = self._create_datapoints()
        self._add_missing_concepts()

    def _create_entities(self) -> Dict[str, pd.DataFrame]:
        """
        Create a list of dicts mapping from entity names to entity frames.

        If the entity exists in the data ontology, merge it. Else just use `data`.

        Returns
        -------
        list
            List of dicts mapping entity name -> entity frame.
        """
        items: dict = dict()
        for entity in self.data.ddf.entities:
            frame = self.data.ddf.create_entity_frame(entity)
            frame = self._hydrate_entity(frame, entity)
            items[entity] = frame
        return items

    def _create_datapoints(self) -> dict:
        items: dict = dict()
        for measures, keys in self.data.ddf.datapoints:
            frame = self.data[measures + keys]
            items[f'ddf--datapoints--{"--".join(measures)}--by--{"--".join(keys)}.csv'] = frame
        return items

    def _add_missing_concepts(self) -> None:
        """
        Recursively add missing concepts, e.g. entities referred to in other entities.
        """
        finished = False
        while not finished:
            missing: list = []
            concepts = self.concepts.copy()
            for entity_name, entity_frame in self.entities.items():
                cols = self._create_concepts(entity_frame)
                missing_frame = cols[~cols.concept.isin(concepts.concept)]
                missing.extend(missing_frame.concept.to_list())
            for col in concepts.columns:
                if col in ['concept', 'concept_type']:
                    continue
                if not (concepts.concept == col).any():
                    missing.append(col)
            if not missing:
                finished = True
            else:
                for miss in missing:
                    self.concepts = self.concepts.append({'concept': miss}, ignore_index=True)
                    self.concepts = self._hydrate_concepts(self.concepts)
                    row = self.concepts[self.concepts.concept == miss].iloc[0]
                    if row.concept_type == 'entity_domain':
                        self.entities[miss] = read_entity(miss)

    def _create_concepts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create a DDF concepts dataframe from a given dataframe.

        The resulting dataframe will have only a `concept` column.

        Parameters
        ----------
        df : pd.DataFrame
            Input dataframe.

        Returns
        -------
        pd.DataFrame
            A simplied DDF concepts dataframe.
        """
        # Split columns by period to handle composite concepts
        cols = pd.Series(df.columns).str.split('.', expand=True)
        cols = pd.concat([cols[i] for i in range(cols.shape[1])])
        cols = pd.Series(cols).str.split('__', expand=True)
        cols = pd.concat([cols[i] for i in range(cols.shape[1])])
        cols = cols.dropna().drop_duplicates()

        return cols.to_frame(name='concept')

    def _hydrate_concepts(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge `df` with ontology concepts, adding extra columns.

        Parameters
        ----------
        df : pd.DataFrame
            Input dataframe.

        Returns
        -------
        pd.DataFrame
            Merged dataframe.
        """
        return df[['concept']].merge(read_concepts(*df.concept.to_list(), recursive=False),
                                     on='concept',
                                     how='left')

    def _hydrate_entity(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        """
        Merge `df` with corresponding entity frame in the ontology, adding extra columns.

        Parameters
        ----------
        df : pd.DataFrame
            Input dataframe.
        name : str
            Name of entity.

        Returns
        -------
        pd.DataFrame
            Merged dataframe.
        """
        if not entity_exists(name):
            return df
        return df[[name]].merge(read_entity(name), on=name, how='left')

    def save(self, path: Union[Path, str], **kwargs: str) -> None:
        """
        Save the data as a DDF data package.

        Parameters
        ----------
        path : str or pathlib.Path
            Directory path.
        **kwargs
            Any additional keyword arguments are treated as package metadata.
        """
        files: dict = dict()

        path = Path(path)
        if path.exists():
            shutil.rmtree(path)
        path.mkdir()

        # Prepare ddf--concepts
        files['ddf--concepts.csv'] = self.concepts

        # Prepare entity domain files
        for entity_name, entity_frame in self.entities.items():
            files[f'ddf--entities--{entity_name}.csv'] = entity_frame

        # Prepare datapoints files
        for data_name, data_frame in self.datapoints.items():
            files[data_name] = data_frame

        # Write all files to disk
        for fname, frame in files.items():
            frame.to_csv(path / fname, index=False)

        # Populate the package metadata object
        kwargs['status'] = kwargs.get('status', 'draft')
        kwargs['title'] = kwargs.get('title', kwargs.get('name', ''))
        kwargs['topics'] = kwargs.get('topics', [])  # type: ignore
        kwargs['default_measure'] = kwargs.get('default_measure', '')
        kwargs['default_primary_key'] = '--'.join(
            sorted(kwargs.get('default_primary_key', [])))
        kwargs['author'] = kwargs.get('author', 'Datastory')

        # Create datapackage.json
        meta = package.create_datapackage(path, **kwargs)
        dump_json(path / 'datapackage.json', meta)

        log.info('Validating package on disk')
        validate_package(path)
