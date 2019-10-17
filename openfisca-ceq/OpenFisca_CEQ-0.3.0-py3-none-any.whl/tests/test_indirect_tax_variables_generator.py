import logging


from openfisca_ceq import CountryTaxBenefitSystem as CEQTaxBenefitSystem
from openfisca_ceq.tools.indirect_taxation.consumption_items_nomenclature import (
    build_tax_rate_by_code_coicop,
    build_complete_label_coicop_data_frame,
    build_label_by_code_coicop,
    )
from openfisca_ceq.tools.indirect_taxation.variables_generator import (
    generate_postes_variables,
    generate_depenses_ht_postes_variables,
    generate_fiscal_base_variables,
    generate_ad_valorem_tax_variables,
    )


log = logging.getLogger(__name__)


tax_variables_by_country = {
    "senegal": ['tva']
    }


def add_coicop_item_to_tax_benefit_system(tax_benefit_system, country):
    label_by_code_coicop = (build_label_by_code_coicop(country)
        .filter(['label_variable'])
        .reset_index()
        .rename(columns = {'deduplicated_code_coicop': "code_coicop"})
        .set_index("code_coicop")
        .to_dict()['label_variable']
        )
    log.debug(label_by_code_coicop)
    log.debug(tax_benefit_system.variables.keys())
    generate_postes_variables(tax_benefit_system, label_by_code_coicop)
    tax_variables = tax_variables_by_country.get(country)
    tax_rate_by_code_coicop = build_tax_rate_by_code_coicop(country, tax_variables)

    tax_name = 'tva'
    null_rates = ['exonere']
    generate_depenses_ht_postes_variables(tax_benefit_system, tax_name, tax_rate_by_code_coicop, null_rates)
    generate_fiscal_base_variables(tax_benefit_system, tax_name, tax_rate_by_code_coicop, null_rates)
    generate_ad_valorem_tax_variables(tax_benefit_system, tax_name, tax_rate_by_code_coicop, null_rates)


def main():
    country = "senegal"
    build_complete_label_coicop_data_frame(country)
    tax_benefit_system = CEQTaxBenefitSystem()
    add_coicop_item_to_tax_benefit_system(tax_benefit_system, country)
    log.info(sorted(tax_benefit_system.variables.keys()))


if __name__ == '__main__':
    import sys
    logging.basicConfig(level = logging.INFO, stream = sys.stdout)
    main()
