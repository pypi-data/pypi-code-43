# -*- coding: utf-8 -*-


from openfisca_core.model_api import *
from openfisca_ceq.entities import *


class corporate_income_tax(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Corporate Income Tax"


class customs_duties(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Customs Duties"


class direct_taxes(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Direct Taxes"

    def formula(household, period):
        personal_income_tax = household('personal_income_tax', period)
        corporate_income_tax = household('corporate_income_tax', period)
        payroll_tax = household('payroll_tax', period)
        property_tax = household('property_tax', period)
        other_taxes = household('other_taxes', period)

        direct_taxes = (
            personal_income_tax
            + corporate_income_tax
            + payroll_tax
            + property_tax
            + other_taxes
            )
        return direct_taxes


class excise_taxes(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = " Excise Taxes"


class indirect_taxes(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Indirect taxes"

    def formula(household, period):
        value_added_tax = household('value_added_tax', period)
        sales_tax = household('sales_tax', period)
        excise_taxes = household('excise_taxes', period)
        customs_duties = household('customs_duties', period)

        indirect_taxes = (
            value_added_tax
            + sales_tax
            + excise_taxes
            + customs_duties
            )
        return indirect_taxes


class sales_tax(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = " Sales Tax"


class value_added_tax(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = " Value added tax (VAT)"


class other_taxes(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Other taxes"


class payroll_tax(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Payroll Tax"


class personal_income_tax(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Personal Income Tax"


class property_tax(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Taxes on Property "
