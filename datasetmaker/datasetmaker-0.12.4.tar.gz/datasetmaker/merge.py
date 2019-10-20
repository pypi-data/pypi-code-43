import os
import shutil
import pathlib
from functools import lru_cache
from typing import Union
from pathlib import Path
import ddf_utils
import pandas as pd
from datasetmaker.onto.manager import read_entity
from datasetmaker.datapackage import DataPackage
from datasetmaker.utils import CSV_DTYPES


def merge_packages(paths: list, dest: Union[Path, str], **kwargs: Union[str, list]) -> None:
    """
    Merge multiple DDF packages into one.

    Parameters
    ----------
    paths : list
        List of paths or in-memory packages
    dest : str
        Path to destination DDF package.
    kwargs :
        Metadata for resulting DDF package.
    """
    if isinstance(paths[0], DataPackage):
        tmp_dir = Path('.tmp_packages')
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir()
        for i, package in enumerate(paths):
            package.save(tmp_dir / f'data_{i}')
        merge_packages([tmp_dir / f'data_{i}' for i in range(i + 1)], dest)
        shutil.rmtree(tmp_dir)
        return

    dest = pathlib.Path(dest)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir()

    paths = [pathlib.Path(x) for x in paths]
    for path in paths:
        dst_files = [x.name for x in dest.glob('*.csv')]
        src_files = path.glob('*.csv')
        for src_file in src_files:
            if src_file.name in dst_files:
                if 'ddf--entities' in src_file.name:
                    src_df = pd.read_csv(src_file, dtype=CSV_DTYPES)
                    dst_df = pd.read_csv(dest / src_file.name, dtype=CSV_DTYPES)
                    df = pd.concat([src_df, dst_df], sort=True)
                    df = df.drop_duplicates(subset=src_file.stem.split('--')[-1])
                    df.to_csv(dest / src_file.name, index=False)
                elif 'ddf--concepts' in src_file.name:
                    src_df = pd.read_csv(src_file, dtype=CSV_DTYPES)
                    dst_df = pd.read_csv(dest / src_file.name, dtype=CSV_DTYPES)
                    df = pd.concat([src_df, dst_df], sort=True)
                    df = df.drop_duplicates(subset='concept')
                    df.to_csv(dest / src_file.name, index=False)
                else:
                    raise ValueError('Duplicate datapoints files')
            else:
                shutil.copy(src_file, dest / src_file.name)

    meta = ddf_utils.package.create_datapackage(dest, **kwargs)
    ddf_utils.io.dump_json(dest / 'datapackage.json', meta)


# def merge_packages(paths: list,
#                    dest: Union[Path, str],
#                    include: list = []) -> None:
#     collection = DDFPackageCollection(paths)
#     collection.to_package(dest, include)


def filter_items(items: Union[pd.DataFrame, list],
                 include: list) -> Union[pd.DataFrame, list]:
    """
    Filter items by include.

    Parameters
    ----------
    items : list or DataFrame, sequence to be filtered. If DataFrame,
        assumed to be a DDF concepts file filtered by concept column.
    include : sequence of labels to include in items
    """
    if not include:
        return items
    if type(items) is list:
        if "--" not in items[0]:  # not datapoints
            return filter(lambda x: x in include, items)
        out = []
        for item in items:
            name = item.split("--")[2:]
            name.pop(1)
            if all([x in include for x in name]):
                out.append(item)
        return out
    # Items is dataframe
    return items[items.concept.isin(include)]  # type: ignore


class DDFPackage:
    """
    Thin wrapper for DDF datapackages.

    Parameters
    ----------
    path : string, path to package directory
    """

    def __init__(self, path: Union[Path, str]):
        self.path = path
        self.meta = ddf_utils.package.get_datapackage(path)

    @lru_cache()
    def read_concepts(self) -> pd.DataFrame:
        path = os.path.join(self.path, "ddf--concepts.csv")
        return pd.read_csv(path)

    def list_entities(self) -> list:
        entities = self.meta["ddfSchema"]["entities"]
        return [x["primaryKey"][0] for x in entities]

    def list_datafiles(self) -> list:
        datapoints = self.meta["ddfSchema"]["datapoints"]
        # TODO: Might be multiple resources here
        return [x["resources"][0] for x in datapoints]

    def read_datafile(self, name: str) -> pd.DataFrame:
        path = os.path.join(self.path, f"{name}.csv")
        return pd.read_csv(path)

    def read_entity(self, name: str) -> pd.DataFrame:
        path = os.path.join(self.path, f"ddf--entities--{name}.csv")
        return pd.read_csv(path)

    def __contains__(self, concept: str) -> bool:
        concepts = self.read_concepts()
        return (concepts.concept == concept).any()


class DDFPackageCollection:
    """
    Shared methods for querying and transforming a set of DDF packages.

    Parameters
    ----------
    paths : list, paths to package directories
    """

    def __init__(self, paths: list):
        self.paths = paths
        self.packages = [DDFPackage(x) for x in paths]

    def create_common_concepts_frame(self) -> pd.DataFrame:
        df = pd.concat([x.read_concepts() for x in self.packages], sort=True)
        df = df.drop_duplicates(subset=["concept"])
        return df

    def list_shared_entities(self) -> set:
        entities = [set(x.list_entities()) for x in self.packages]
        return set.intersection(*entities)

    def list_distinct_entities(self) -> set:
        entities = [set(x.list_entities()) for x in self.packages]
        sym_diff = entities[0]
        for entity in entities[1:]:
            sym_diff.symmetric_difference_update(entity)
        return sym_diff

    def list_datafiles(self) -> list:
        datapoints = []
        for package in self.packages:
            datapoints.extend(package.list_datafiles())
        return datapoints

    def create_entity_frame(self, name: str) -> pd.DataFrame:
        frames = []
        for package in self.packages:
            if name not in package.list_entities():
                continue
            frames.append(package.read_entity(name))
        df = pd.concat(frames, sort=True).drop_duplicates(subset=name)
        entity_frame = read_entity(name)
        if isinstance(entity_frame, pd.DataFrame):
            df = df.merge(entity_frame,
                          on=name,
                          suffixes=('_x', ''),
                          how='outer')
            df = df.drop([x for x in df.columns if x.endswith('_x')], axis=1)
        return df

    def create_datapoint_frame(self, name: str) -> pd.DataFrame:
        frames = []
        for package in self.packages:
            if name not in package.list_datafiles():
                continue
            frames.append(package.read_datafile(name))
        return pd.concat(frames, sort=True)

    def to_package(self, dest: Union[Path, str], include: list = []) -> None:
        shutil.rmtree(dest, ignore_errors=True)
        os.mkdir(dest)

        concepts = filter_items(self.create_common_concepts_frame(), include)
        path = os.path.join(dest, "ddf--concepts.csv")
        concepts.to_csv(path, index=False)  # type: ignore

        for se in filter_items(self.list_shared_entities(), include):
            df = self.create_entity_frame(se)
            path = os.path.join(dest, f"ddf--entities--{se}.csv")
            df.to_csv(path, index=False)

        for de in filter_items(self.list_distinct_entities(), include):
            df = self.create_entity_frame(de)
            path = os.path.join(dest, f"ddf--entities--{de}.csv")
            df.to_csv(path, index=False)

        for datafile in filter_items(self.list_datafiles(), include):
            df = self.create_datapoint_frame(datafile)
            path = os.path.join(dest, f"{datafile}.csv")
            df.to_csv(path, index=False)

        meta = ddf_utils.package.create_datapackage(dest)
        ddf_utils.io.dump_json(os.path.join(dest, "datapackage.json"), meta)
