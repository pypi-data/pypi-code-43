from typing import Dict, List, TypeVar, Optional

import numpy as np
import pandas as pd


T = TypeVar('T')


def infer_design_matrix(
    data_dict: Dict[str, List[T]],
    feature_value_dict: Optional[Dict[str, Dict[T, float]]] = None,
    default_value: float = 0
) -> pd.DataFrame:
    """ Convert mapping of the form `{'sample_id': [<data>]}`
        to a design matrix (<n_samples>x<n_features>).
    """
    # generate spaces
    sample_space = np.asarray(list(sorted(data_dict.keys())))
    feature_space = np.asarray(list(sorted(
        set([g for gs in data_dict.values() for g in gs]))))

    n_samples = len(data_dict)
    n_features = len(feature_space)

    # fill in data
    mat = np.full((n_samples, n_features), default_value, dtype=float)
    for i, sample in enumerate(sample_space):
        cur_features = data_dict[sample]
        idx = [np.argwhere(feature_space == v)[0, 0]
               for v in cur_features]

        idx_val = 1 if feature_value_dict is None \
            else [feature_value_dict[sample][v] for v in cur_features]
        mat[i, idx] = idx_val

    return pd.DataFrame(mat.T, index=feature_space, columns=sample_space)
