import configparser
import logging
import os
import pandas as pd


from openfisca_survey_manager import default_config_files_directory as config_files_directory
from openfisca_ceq.tools.data_ceq_correspondence import (
    ceq_input_by_harmonized_variable,
    ceq_intermediate_by_harmonized_variable,
    data_by_model_weight_variable,
    model_by_data_id_variable,
    non_ceq_input_by_harmonized_variable,
    variables_by_entity,
    )


log = logging.getLogger(__name__)


config_parser = configparser.ConfigParser()
config_parser.read(os.path.join(config_files_directory, 'raw_data.ini'))

year_by_country = {
    # 'mali': 2014,
    'senegal': 2011,
    }


missing_revenus_by_country = {
    'mali': [
        'rev_i_independants_taxe',
        'rev_i_independants_Ntaxe',
        'rev_i_locatif',
        'rev_i_autres_revenus_capital',
        'rev_i_pensions',
        'rev_i_transferts_publics',
        ],
    }


def build_income_dataframes(country):
    year = year_by_country[country]
    income_data_path = config_parser.get(country, 'revenus_harmonises_{}'.format(year))
    model_variable_by_person_variable = dict()
    variables = [
        ceq_input_by_harmonized_variable,
        ceq_intermediate_by_harmonized_variable,
        model_by_data_id_variable,
        non_ceq_input_by_harmonized_variable,
        ]
    for d in variables:
        model_variable_by_person_variable.update(d)

    income = pd.read_stata(income_data_path)

    for var in income.columns:
        if var.startswith("rev"):
            assert income[var].notnull().any(), "{} income variable for {} is all null".format(var, country)

    assert (
        set(model_variable_by_person_variable.keys()).difference(
            set(missing_revenus_by_country.get(country, []))
            )
        <= set(income.columns)
        ), \
        "Missing {} in {} income data source".format(
            country,
            set(model_variable_by_person_variable.keys()).difference(
                set(missing_revenus_by_country.get(country, []))
                ).difference(set(income.columns))
            )

    data_by_model_id_variable = {v: k for k, v in model_by_data_id_variable.items()}

    dataframe_by_entity = dict()
    for entity, variables in variables_by_entity.items():
        filtered_variables = list(
            set(variables).difference(
                set(missing_revenus_by_country.get(country, [])))
            )

        dataframe_by_entity[entity] = income[
            filtered_variables
            + [
                data_by_model_id_variable["{}_id".format(entity)],
                data_by_model_weight_variable["{}_weight".format(entity)],
                ]

            ]

    return dataframe_by_entity["person"], dataframe_by_entity["household"]


if __name__ == "__main__":
    for country in year_by_country.keys():
        person_dataframe, household_dataframe = build_income_dataframes(country)
