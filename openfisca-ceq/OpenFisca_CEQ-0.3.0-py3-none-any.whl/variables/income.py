# -*- coding: utf-8 -*-


from openfisca_core.model_api import *
from openfisca_ceq.entities import *


# This variable is a pure input: it doesn't have a formula


class alimony(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Alimony"


class all_income_excluding_transfers(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Earned and Unearned Incomes of All Possible Sources and Excluding Government Transfers"


class autoconsumption(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Autoconsumption"


class consumable_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Consumable income"

    def formula(household, period):
        disposable_income = household('disposable_income', period)
        indirect_subsidies = household('indirect_subsidies', period)
        indirect_taxes = household('indirect_taxes', period)
        consumable_income = disposable_income + indirect_subsidies - indirect_taxes
        return consumable_income


class disposable_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Disposable income"

    def formula(household, period):
        net_market_income = household('net_market_income', period)
        direct_transfers = household('direct_transfers', period)
        disposable_income = net_market_income + direct_transfers
        return disposable_income


class final_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Final income"

    def formula(household, period):
        consumable_income = household('consumable_income', period)
        in_kind_transfers = household('in_kind_transfers', period)
        final_income = consumable_income + in_kind_transfers
        return final_income


class gifts_sales_durables(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Gifts, proceeds from sale of durables"


class gross_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Gross income"

    def formula(household, period):
        market_income_plus_pensions = household('market_income_plus_pensions', period)
        direct_transfers = household('direct_transfers', period)
        gross_income = market_income_plus_pensions + direct_transfers
        return gross_income


class imputed_rent(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Imputed rent for owner occupied housing"


class nontaxable_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Nontaxable income"


class market_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Market income"

    def formula(household, period):
        all_income_excluding_transfers = household('all_income_excluding_transfers', period)
        gifts_sales_durables = household('gifts_sales_durables', period)
        alimony = household('alimony', period)
        autoconsumption = household('autoconsumption', period)
        imputed_rent = household('imputed_rent', period)
        other_income = household('other_income', period)

        market_income = (
            all_income_excluding_transfers
            + gifts_sales_durables
            + alimony
            + autoconsumption
            + imputed_rent
            + other_income
            )
        return market_income


class market_income_plus_pensions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Market income plus net pensions"

    def formula(household, period):
        market_income = household('market_income', period)
        pensions = household('pensions', period)
        contributions_pensions = household('contributions_pensions', period)
        market_income_plus_pensions = (
            market_income
            + pensions
            - contributions_pensions
            )
        return market_income_plus_pensions


class net_market_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Net market income"

    def formula(household, period):
        market_income_plus_pensions = household('market_income_plus_pensions', period)
        direct_taxes = household('direct_taxes', period)
        contributions_health = household('contributions_health', period)

        net_market_income = (
            market_income_plus_pensions
            - (
                direct_taxes
                + contributions_health
                )
            )
        return net_market_income


class other_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Other sources of income"


class pensions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Old-age contributory pensions"


class taxable_income(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Taxable income"

    def formula(household, period):
        gross_income = household('gross_income', period)
        nontaxable_income = household('nontaxable_income', period)
        taxable_income = gross_income - nontaxable_income
        return taxable_income
