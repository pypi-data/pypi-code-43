import json
import pandas as pd
from os import getenv
from collections import OrderedDict, defaultdict


def getBiasedDataset(data: pd.DataFrame, biases: dict) -> pd.DataFrame:
    df = pd.DataFrame()
    for key in biases:
        df_bias = pd.DataFrame.from_dict(biases[key], orient='index', columns=['bias'])
        df_data = pd.DataFrame(data.groupby(by=f'{key}').size(), columns=['Vol']).reset_index().set_index(key)

        df_processing = df_data.join(df_bias)
        df_processing["Ratio"] = df_processing["Vol"]/df_processing["bias"]
        df_processing["Output"] = df_processing["Ratio"].min() * df_processing["bias"]
        dict_n = df_processing["Output"].astype(int).to_dict(OrderedDict)

        count = 1
        namespace = globals()
        ds = pd.DataFrame()

        for v in dict_n:
            namespace[f'ds_{count}'] = data[data[key].isin([v])].sample(n=dict_n[v])
            ds = ds.append(namespace[f'ds_{count}'])
            count += 1
        data = ds
    return data