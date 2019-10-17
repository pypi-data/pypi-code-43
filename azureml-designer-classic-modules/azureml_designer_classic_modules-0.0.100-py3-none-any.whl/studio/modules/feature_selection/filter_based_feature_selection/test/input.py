from pathlib import Path

import pandas as pd

from azureml.studio.common.datatable.data_table import DataTable


def input_dt_german_credit_card_uci():
    df = pd.read_csv(Path(__file__).parent / 'input/german_credit_card_uci_data.csv')
    return DataTable(df)


def input_dt_adult_census_income():
    df = pd.read_csv(Path(__file__).parent / 'input/adult_census_income_data.csv')
    return DataTable(df)
