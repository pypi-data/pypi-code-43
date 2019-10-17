# -*- coding: utf-8 -*-


from openfisca_core.model_api import *
from openfisca_ceq.entities import *


class indirect_subsidies(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Indirect subsidies"

    def formula(household, period):
        electricity_subsidies = household('electricity_subsidies', period)
        fuel_subsidies = household('fuel_subsidies', period)
        food_subsidies = household('food_subsidies', period)
        agricultural_inputs_subsidies = household('agricultural_inputs_subsidies', period)
        indirect_subsidies = (
            electricity_subsidies
            + fuel_subsidies
            + food_subsidies
            + agricultural_inputs_subsidies
            )
        return indirect_subsidies


class agricultural_inputs_subsidies(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = " Agricultural Inputs subsidies"


class electricity_subsidies(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = "Electricity subsidies"


class food_subsidies(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = " Food subsidies"


class fuel_subsidies(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    label = " Fuel subsidies"
