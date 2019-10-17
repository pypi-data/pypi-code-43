# -*- coding: utf-8 -*-


from openfisca_core.model_api import *
from openfisca_ceq.entities import *


class cash_transfers(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Conditional and Unconditional Cash Transfers"


class direct_transfers(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Direct transfers (social protection)"

    def formula(household, period):
        social_assistance = household('social_assistance', period)
        social_insurance = household('social_insurance', period)
        direct_transfers = social_assistance + social_insurance
        return direct_transfers


class near_cash_transfers(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Near Cash Transfers (Food, School Uniforms, etc.)"


class noncontributory_pensions(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Noncontributory Pensions"


class social_assistance(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Social Assistance"

    def formula(household, period):
        cash_transfers = household('cash_transfers', period)
        noncontributory_pensions = household('noncontributory_pensions', period)
        near_cash_transfers = household('near_cash_transfers', period)

        social_assistance = cash_transfers + noncontributory_pensions + near_cash_transfers
        return social_assistance


class social_insurance(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Social Insurance"
