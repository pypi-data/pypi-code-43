from types import ModuleType

import pandas as pd

from ._model import _AssetBase


def build(model, metadata):
    return pd.DataFrame(_build(model, metadata))


def _build(model, metadata):
    results = list()

    if isinstance(model, ModuleType):
        if 'Build Path' not in metadata or 'Build Asset' not in metadata or 'Build Template' not in metadata:
            raise RuntimeError('"Build Path", "Build Asset", "Build Template" are required columns')
        unique_assets = metadata[['Build Path', 'Build Asset', 'Build Template']].drop_duplicates().dropna()
        columns_to_drop = ['Build Path', 'Build Asset', 'Build Template']
    elif issubclass(model, _AssetBase):
        if 'Build Path' not in metadata or 'Build Asset' not in metadata:
            raise RuntimeError('"Build Path", "Build Asset" are required columns')
        if 'Build Template' in metadata:
            raise RuntimeError('"Build Template" not allowed when "model" parameter is Asset/Mixin class '
                               'declaration')
        unique_assets = metadata[['Build Path', 'Build Asset']].drop_duplicates().dropna()
        columns_to_drop = ['Build Path', 'Build Asset']
    else:
        raise RuntimeError('"model" parameter must be a Python module (with Assets/Mixins) or an Asset/Mixin class '
                           'declaration')

    for index, row in unique_assets.iterrows():
        if isinstance(model, ModuleType):
            template = getattr(model, row['Build Template'].replace(' ', '_'))
        else:
            template = model

        instance = template({
            'Name': row['Build Asset'],
            'Asset': row['Build Asset'],
            'Path': row['Build Path']
        })

        instance_metadata = metadata[(metadata['Build Asset'] == row['Build Asset']) &
                                     (metadata['Build Path'] == row['Build Path'])]

        results.extend(instance.build(instance_metadata))

    results_df = pd.DataFrame(results)

    return results_df.drop(columns=columns_to_drop, errors='ignore')
