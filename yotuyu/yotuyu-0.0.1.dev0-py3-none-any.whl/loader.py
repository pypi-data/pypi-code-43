from pathlib import Path

import pandas as pd


def load_csv(file_name):
    sample_file = Path.cwd() / Path(f'data/{file_name}')
    return __load_sample_data(sample_file)


def __load_sample_data(sample_file):
    df = pd.read_csv(str(sample_file))
    return df
