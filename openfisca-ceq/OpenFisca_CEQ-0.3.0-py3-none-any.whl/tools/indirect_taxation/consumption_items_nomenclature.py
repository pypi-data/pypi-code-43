import configparser
import logging
import os
import pandas as pd
import pkg_resources


from openfisca_survey_manager.coicop import build_raw_coicop_nomenclature
from openfisca_survey_manager import default_config_files_directory as config_files_directory


log = logging.getLogger(__name__)


config_parser = configparser.ConfigParser()
config_parser.read(os.path.join(config_files_directory, 'raw_data.ini'))
consumption_items_directory = config_parser.get('ceq', 'consumption_items_directory')
assert os.path.exists(consumption_items_directory), \
    "Consumption items directory {} does not exists, please create it and fill it with countries consumption items files"


country_code_by_country = {
    "mali": "MLI",
    "senegal": "SEN",
    "cote_d_ivoire": "CIV",
    }


def build_label_by_code_coicop(country, additional_variables = None):
    consumption_items_file_path = os.path.join(
        consumption_items_directory, "Produits_{}.xlsx".format(country_code_by_country[country])
        )
    if additional_variables is None:
        additional_variables = []
    consumption_items = pd.read_excel(consumption_items_file_path)
    label_by_code_coicop = (consumption_items
        .rename(
            columns = {
                'label': 'label_variable',
                'nom_variable_format_wide': 'variable_name'
                }
            )
        .filter(['label_variable', 'code_coicop', 'variable_name'] + additional_variables)
        .dropna()
        .astype(str)
        .sort_values('code_coicop')
        )
    label_by_code_coicop['code_coicop'] = label_by_code_coicop.code_coicop.str.strip("0")
    duplicated_coicop = label_by_code_coicop.loc[label_by_code_coicop.code_coicop.duplicated()]
    label_by_code_coicop['deduplicated_code_coicop'] = label_by_code_coicop.code_coicop.copy()
    for code_coicop in duplicated_coicop.code_coicop.unique():
        n = sum(label_by_code_coicop.code_coicop == code_coicop)
        alphabet = 'abcdefghijklmnopqrstuvwxyz'
        enhanced_code_coicops = [code_coicop + '.' + alphabet[i] for i in range(n)]
        label_by_code_coicop.loc[label_by_code_coicop.code_coicop == code_coicop, 'deduplicated_code_coicop'] = enhanced_code_coicops

    assert not label_by_code_coicop.deduplicated_code_coicop.duplicated().any()
    label_by_code_coicop = (label_by_code_coicop
        .set_index('deduplicated_code_coicop')
        )
    return label_by_code_coicop


def build_complete_label_coicop_data_frame(country, file_path = None, deduplicate = True):
    label_by_code_coicop = build_label_by_code_coicop(country)
    raw_coicop_nomenclature = build_raw_coicop_nomenclature()
    completed_label_coicop = (label_by_code_coicop
        .reset_index()
        .merge(raw_coicop_nomenclature, on = 'code_coicop', how = 'left')
        .filter(items = [
            'label_division',
            'label_groupe',
            'label_classe',
            'label_sous_classe',
            'label_poste',
            'label_variable',
            'code_coicop',
            'deduplicated_code_coicop',
            ])
        )

    if deduplicate:
        completed_label_coicop = (completed_label_coicop
            .drop('code_coicop', axis = 1)
            .rename(columns = {'deduplicated_code_coicop': "code_coicop"})
            )

    if file_path:
        completed_label_coicop.to_csv(file_path)
    return completed_label_coicop


def build_comparison_table(countries):
    dfs = [
        build_complete_label_coicop_data_frame(country, deduplicate = False)
        for country in countries
        ]

    index = [
        'label_division',
        'label_groupe',
        'label_classe',
        'label_sous_classe',
        'label_poste',
        'code_coicop'
        ]

    dfs = [
        df.groupby(index)['label_variable'].unique()
        for df in dfs
        ]

    merged = pd.concat(dfs, axis = 1, keys = country_code_by_country.values(), join = 'outer', copy = False).reset_index()
    merged['division_index'] = merged.code_coicop.str.split('.', 1).str[0].astype(int)
    merged = (merged.sort_values(['division_index', 'code_coicop']).drop('division_index', axis = 1))
    assets_directory = os.path.join(
        pkg_resources.get_distribution('openfisca-ceq').location,
        'openfisca_ceq',
        'assets'
        )
    merged.to_csv(os.path.join(assets_directory, 'merged.csv'))
    merged.to_excel(os.path.join(assets_directory, 'merged.xls'))

    return merged


def build_tax_rate_by_code_coicop(country, tax_variables = None):
    assert tax_variables is not None
    label_by_code_coicop = (build_label_by_code_coicop(country, additional_variables = tax_variables)
        .drop(columns = "code_coicop")
        .reset_index()
        .rename(columns = {'deduplicated_code_coicop': "code_coicop"})
        )
    assert "code_coicop" in label_by_code_coicop.columns
    return label_by_code_coicop


if __name__ == '__main__':
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    tax_variables_by_country = {
        "senegal": ['tva']
        }
    country = "senegal"
    tax_variables = tax_variables_by_country.get(country, [])
    df = build_tax_rate_by_code_coicop(country, tax_variables)
    for tax_variable in tax_variables:
        log.info(tax_variable + "\n" + str(df[tax_variable].value_counts()))
    # countries = ['cote_d_ivoire', 'senegal', 'mali']
    # merged = build_comparison_table(countries)
