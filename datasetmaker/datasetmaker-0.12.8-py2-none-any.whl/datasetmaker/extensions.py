from collections import defaultdict
from typing import Optional, List, Dict, Tuple, Union
import pandas as pd


@pd.api.extensions.register_dataframe_accessor('ddf')
class DDFAccessor:
    """
    Custom dataframe accessor for keeping track of DDF concepts in frames.
    """

    def __init__(self, pandas_obj: pd.DataFrame):
        self._validate(pandas_obj)
        self._obj = pandas_obj
        self._entities: List = list()
        self._properties: Dict = dict()
        self._datapoints: List[Tuple] = list()
        self._roles: Dict = defaultdict(list)

    @staticmethod
    def _validate(obj: pd.DataFrame) -> None:
        pass

    def _find_entity_cols(self, key: str) -> list:
        """
        Locate columns with domain `key`.
        """
        out_cols = []
        cols = self._obj.columns.to_list()
        for col in cols:
            components = col.split('.')[-1].split('__')
            if key in components:
                out_cols.append(col)
            else:
                for role in self.roles.get(key, []):
                    if role in components:
                        out_cols.append(col)
        return list(set(out_cols))

    def register_entity(self, key: str, props: list = [], roles: list = []) -> None:
        if key not in self._entities:
            self._entities.append(key)
        for role in roles:
            self._roles[key].append(role)
        for prop in props:
            self.register_property(prop, key)

    def unregister_entity(self, key: str) -> None:
        if key in self._entities:
            self._entities.remove(key)

    def create_entity_frame(self, key: str) -> Optional[pd.DataFrame]:
        if key not in self._entities:
            return None

        cols = self._find_entity_cols(key)

        frames = []
        for col in cols:
            dunder_props = [x for x in self._obj.columns if x.startswith(f'{col}__')]
            frame = self._obj[[col] + dunder_props]
            frame.columns = [x.split('__')[-1].split('.')[-1] for x in frame.columns]
            frames.append(frame)

        df = pd.concat(frames, sort=True)

        if key not in df:
            df[key] = None
        for role in self.roles.get(key, []):
            df[key] = df[key].fillna(df[role])
            df = df.drop(role, axis=1)

        if key not in self._properties:
            return df.drop_duplicates(subset=key).dropna(subset=[key]).reset_index(drop=True)

        return (df
                .merge(self._obj[self._properties[key]], left_index=True, right_index=True)
                .drop_duplicates(subset=key)
                .dropna(subset=[key])
                .reset_index(drop=True))

    @property
    def entities(self) -> list:
        """
        Registered entities.
        """
        return self._entities

    def register_property(self, prop: str, entity: str) -> None:
        if entity not in self._properties:
            self._properties[entity] = [prop]
        else:
            if prop not in self._properties[entity]:
                self._properties[entity].append(prop)

    def unregister_property(self, prop: str, entity: str) -> None:
        if entity not in self._properties:
            return
        if prop in self._properties[entity]:
            self._properties[entity].remove(prop)

    @property
    def properties(self) -> dict:
        """
        Registered properties.
        """
        return self._properties

    def register_datapoints(self, measures: Union[str, list], keys: Union[str, list]) -> None:
        if type(keys) is str:
            keys = [keys]
        if type(measures) is str:
            measures = [measures]
        self._datapoints.append((measures, keys))

    @property
    def datapoints(self) -> list:
        """
        Registered datapoints.
        """
        return self._datapoints

    @property
    def roles(self) -> dict:
        """
        Registered roles.
        """
        return self._roles
