# -*- coding: utf-8 -*-


from openfisca_core.model_api import *
from openfisca_ceq.entities import *


class other_contributions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Total contributions to social security for other contributory programs (such as unemployment insurance)"

    def formula(household, period):
        employee_other_contributions = household('employee_other_contributions', period)
        employer_other_contributions = household('employer_other_contributions', period)
        self_employed_other_contributions = household('self_employed_other_contributions', period)

        other_contributions = (
            employer_other_contributions
            + employee_other_contributions
            + self_employed_other_contributions
            )
        return other_contributions


class contributions_health(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Total contributions to social security for health"

    def formula(household, period):
        employee_contributions_health = household('employee_contributions_health', period)
        employer_contributions_health = household('employer_contributions_health', period)
        self_employed_contributions_health = household('self_employed_contributions_health', period)
        contributions_health = (
            employee_contributions_health
            + employer_contributions_health
            + self_employed_contributions_health
            )
        return contributions_health


class contributions_pensions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Total contributions to social security for old-age pensions"

    def formula(household, period):
        employee_contributions_pensions = household('employee_contributions_pensions', period)
        employer_contributions_pensions = household('employer_contributions_pensions', period)
        self_employed_contributions_pensions = household('self_employed_contributions_pensions', period)
        contributions_pensions = (
            employee_contributions_pensions
            + employer_contributions_pensions
            + self_employed_contributions_pensions
            )
        return contributions_pensions


class employee_contributions_health(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Employee contributions to social security for health"


class employee_contributions_pensions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Employee contributions to social security for old-age pensions"


class employee_other_contributions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = " Employee contributions to social security for other contributory programs (such as unemployment insurance)"


class employer_contributions_health(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Employer contributions to social security for health"


class employer_contributions_pensions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Employer contributions to social security for old-age pensions"


class employer_other_contributions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Employer contributions to social security for other contributory programs (such as unemployment insurance and others)"


class self_employed_contributions_health(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Self-employed contributions to social security for health"


class self_employed_contributions_pensions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Self-employed contributions to social security for old-age pensions"


class self_employed_other_contributions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Self-employed contributions to social security for other contributory programs (such as unemployment insurance)"
