# -*- coding: utf-8 -*-


from slugify import slugify
import logging


from openfisca_core.model_api import Variable, YEAR


log = logging.getLogger(__name__)


GLOBAL_YEAR_START = 1994
GLOBAL_YEAR_STOP = 2019


def generate_postes_variables(tax_benefit_system, label_by_code_coicop):
    """Generate COICOP item of consumption (poste de cpnsommation)

    :param TaxBenfitSystem tax_benefit_system: the tax and benefit system to create the items variable for
    :param dict label_by_code_coicop: Coicop item number and item description
    """
    for code_coicop, label in label_by_code_coicop.items():
        class_name = "poste_{}".format(slugify(code_coicop, separator = '_'))
        log.info('Creating variable {} with label {}'.format(class_name, label))
        # Trick to create a class with a dynamic name.
        entity = tax_benefit_system.entities_by_singular()['household']
        tax_benefit_system.add_variable(
            type(class_name, (Variable,), dict(
                definition_period = YEAR,
                entity = entity,
                label = label,
                value_type = float,
                ))
            )


def generate_depenses_ht_postes_variables(tax_benefit_system, tax_name, tax_rate_by_code_coicop, null_rates = []):
    """Create depenses_ht_poste_code_coicop variables for every code_coicop
    assuming no code coicop dies and resucitates over time

    :param tax_benefit_system: the tax benefit system that will host the generated variables
    :type tax_benefit_system: TaxBenefitSystem
    :param tax_name: The name of the proportional ad valorem tax
    :type tax_name: str
    :param tax_rate_by_code_coicop: The tax rates for every COICOP code
    :type tax_rate_by_code_coicop: DataFrame
    :param null_rates: The values of the tax rates corresponding to exemption, defaults to []
    :type null_rates: list, optional
    """
    # Almost identical to openfisca-france-indirect-taxation eponymous function
    reference_rates = sorted(tax_rate_by_code_coicop[tax_name].unique())

    functions_by_name_by_poste = dict()
    postes_coicop_all = set()

    for tax_rate in reference_rates:
        functions_by_name = dict()

        time_varying_rates = 'start' in tax_rate_by_code_coicop.columns
        if time_varying_rates:
            start_years = reference_rates.start.fillna(GLOBAL_YEAR_START).unique()
            stop_years = reference_rates.start.fillna(GLOBAL_YEAR_STOP).unique()  # last year
            years_range = sorted(list(set(start_years + stop_years)))
            year_stop_by_year_start = zip(years_range[:-1], years_range[1:])
        else:
            year_stop_by_year_start = {GLOBAL_YEAR_START: GLOBAL_YEAR_STOP}

        for year_start, year_stop in year_stop_by_year_start.items():
            filter_expression = '({} == @tax_rate)'.format(tax_name)
            if time_varying_rates:
                filter_expression += 'and (start <= @year_start) and (stop >= @year_stop)'
            postes_coicop = sorted(
                tax_rate_by_code_coicop.query(filter_expression)['code_coicop'].astype(str)
                )

            log.debug('Creating fiscal category {} - {} (starting in {} and ending in {}) pre-tax expenses for the following products {}'.format(
                tax_name, tax_rate, year_start, year_stop, postes_coicop))

            for poste_coicop in postes_coicop:
                dated_func = depenses_ht_postes_function_creator(
                    poste_coicop,
                    tax_rate,
                    year_start,
                    null_rates,
                    )

                dated_function_name = "formula_{year_start}".format(year_start = year_start)

                if poste_coicop not in functions_by_name_by_poste:
                    functions_by_name_by_poste[poste_coicop] = dict()
                functions_by_name_by_poste[poste_coicop][dated_function_name] = dated_func

            postes_coicop_all = set.union(set(postes_coicop), postes_coicop_all)

    assert set(functions_by_name_by_poste.keys()) == postes_coicop_all

    for poste, functions_by_name in list(functions_by_name_by_poste.items()):
        class_name = 'depenses_ht_poste_{}'.format(slugify(poste, separator = '_'))
        definitions_by_name = dict(
            definition_period = YEAR,
            value_type = float,
            entity = tax_benefit_system.entities_by_singular()['household'],
            label = "Dépenses hors taxe du poste_{}".format(poste),
            )
        definitions_by_name.update(functions_by_name)
        tax_benefit_system.add_variable(
            type(class_name, (Variable,), definitions_by_name)
            )
        del definitions_by_name


def depenses_ht_postes_function_creator(poste_coicop, tax_rate, year_start = None, null_rates = []):
    """Create a function for the pre-tax expense of a particular poste COICOP

    :param poste_coicop: Poste COICOP
    :type poste_coicop: str
    :param parameters: Legislation parameters tree
    :type parameters: ParameterNodetax_rate_by_code_coicop
    :param tax_rate: The name of the applied tax rate
    :type tax_rate: str
    :param year_start: Starting year
    :type year_start: int, optional
    :param null_rates: The values of the tax rates corresponding to exemption, defaults to []
    :type null_rates: list, optional
    :return: pre-tax expense of a particular poste COICO
    :rtype: function
    """
    # Almost identical to openfisca-france-indirect-taxation eponymous function
    assert tax_rate is not None

    def func(entity, period_arg, parameters, tax_rate = tax_rate):
        impots_indirects = parameters(period_arg.start).prelevements_obligatoires.impots_indirects
        if (tax_rate is None) or (tax_rate in null_rates):
            taux = 0
        else:
            taux = impots_indirects.tva[tax_rate]

        return entity('poste_' + slugify(poste_coicop, separator = '_'), period_arg) / (1 + taux)

    func.__name__ = "formula_{year_start}".format(year_start = year_start)
    return func


def depenses_ht_categorie_function_creator(postes_coicop, year_start = None):
    if len(postes_coicop) != 0:
        def func(entity, period_arg):
            return sum(entity(
                'depenses_ht_poste_' + slugify(poste, separator = '_'), period_arg) for poste in postes_coicop
                )

        func.__name__ = "formula_{year_start}".format(year_start = year_start)
        return func

    else:  # To deal with Reform emptying some fiscal categories
        def func(entity, period_arg):
            return 0

    func.__name__ = "formula_{year_start}".format(year_start = year_start)
    return func


def generate_fiscal_base_variables(tax_benefit_system, tax_name, tax_rate_by_code_coicop, null_rates = []):
    reference_rates = sorted(tax_rate_by_code_coicop[tax_name].unique())
    time_varying_rates = 'start' in tax_rate_by_code_coicop.columns
    for tax_rate in reference_rates:
        functions_by_name = dict()
        if time_varying_rates:
            start_years = reference_rates.start.fillna(GLOBAL_YEAR_START).unique()
            stop_years = reference_rates.start.fillna(GLOBAL_YEAR_STOP).unique()  # last year
            years_range = sorted(list(set(start_years + stop_years)))
            year_stop_by_year_start = zip(years_range[:-1], years_range[1:])
        else:
            year_stop_by_year_start = {GLOBAL_YEAR_START: GLOBAL_YEAR_STOP}

        for year_start, year_stop in year_stop_by_year_start.items():
            filter_expression = '({} == @tax_rate)'.format(tax_name)
            if time_varying_rates:
                filter_expression += 'and (start <= @yyear_start) and (stop >= @yyear_stop)'
            postes_coicop = sorted(
                tax_rate_by_code_coicop.query(filter_expression)['code_coicop'].astype(str)
                )

            log.debug('Creating fiscal category {} - {} (starting in {} and ending in {}) aggregate expenses with the following products {}'.format(
                tax_name, tax_rate, year_start, year_stop, postes_coicop))

            dated_func = depenses_ht_categorie_function_creator(
                postes_coicop,
                year_start = year_start,
                )
            dated_function_name = "formula_{year_start}".format(year_start = year_start)
            functions_by_name[dated_function_name] = dated_func

        class_name = 'depenses_ht_{}_{}'.format(tax_name, tax_rate)

        # Trick to create a class with a dynamic name.
        definitions_by_name = dict(
            value_type = float,
            entity = tax_benefit_system.entities_by_singular()['household'],
            label = "Dépenses hors taxes {} - {}".format(tax_name, tax_rate),
            definition_period = YEAR,
            )
        definitions_by_name.update(functions_by_name)
        tax_benefit_system.add_variable(
            type(class_name, (Variable,), definitions_by_name)
            )

        del definitions_by_name


def generate_ad_valorem_tax_variables(tax_benefit_system, tax_name, tax_rate_by_code_coicop, null_rates = []):
    reference_rates = sorted(tax_rate_by_code_coicop[tax_name].unique())
    ad_valorem_tax_components = list()
    for tax_rate in reference_rates:
        functions_by_name = dict()

        log.debug('Creating tax amount {} - {}'.format(tax_name, tax_rate))

        class_name = '{}_{}'.format(tax_name, tax_rate)

        # Trick to create a class with a dynamic name.
        definitions_by_name = dict(
            value_type = float,
            entity = tax_benefit_system.entities_by_singular()['household'],
            label = "{} - {}".format(tax_name, tax_rate),
            definition_period = YEAR,
            )

        def func(entity, period_arg, parameters):
            pre_tax_expenses = entity('depenses_ht_{}_{}'.format(tax_name, tax_rate), period_arg)
            rate = parameters(period_arg).prelevements_obligatoires.impots_indirects.tva[tax_rate]
            return pre_tax_expenses * rate

        func.__name__ = "formula_{year_start}".format(year_start = GLOBAL_YEAR_START)

        functions_by_name[func.__name__] = func
        definitions_by_name.update(functions_by_name)
        tax_benefit_system.add_variable(
            type(class_name, (Variable,), definitions_by_name)
            )

        ad_valorem_tax_components += [class_name]
        del definitions_by_name

    class_name = tax_name

    def ad_valorem_tax_total_func(entity, period_arg):
        return sum(
            entity(class_name, period_arg)
            for class_name in ad_valorem_tax_components
            )

    ad_valorem_tax_total_func.__name__ = "formula_{year_start}".format(year_start = GLOBAL_YEAR_START)
    functions_by_name = dict()
    functions_by_name[func.__name__] = func
    definitions_by_name = dict(
        value_type = float,
        entity = tax_benefit_system.entities_by_singular()['household'],
        label = "{} - total".format(tax_name),
        definition_period = YEAR,
        )
    definitions_by_name.update(functions_by_name)
    tax_benefit_system.add_variable(
        type(class_name, (Variable,), definitions_by_name)
        )
