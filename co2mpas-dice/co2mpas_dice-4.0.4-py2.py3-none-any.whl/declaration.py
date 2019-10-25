#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2014-2018 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
It provides the CO2MPAS validation formulas.
"""
import logging
import schedula as sh

log = logging.getLogger(__name__)

calibration = {
    'VERSION': True,
    'fuel_type': True,
    'engine_fuel_lower_heating_value': True,
    'fuel_carbon_content_percentage': True,
    'ignition_type': True,
    'engine_capacity': True,
    'engine_stroke': True,
    'engine_max_speed': True,
    'idle_engine_speed_median': True,
    'engine_idle_fuel_consumption': True,
    'final_drive_ratio': True,
    'final_drive_ratios': True,
    'tyre_code': True,
    'gear_box_type': True,
    'start_stop_activation_time': True,
    'service_battery_capacity': True,
    'initial_temperature': True,
    'gear_box_ratios': True,
    'full_load_speeds': True,
    'full_load_torques': True,
    'full_load_powers': True,
    'vehicle_mass': True,
    'f0': True,
    'f1': True,
    'f2': True,
    'engine_n_cylinders': True,
    'co2_emission_low': True,
    'co2_emission_medium': True,
    'co2_emission_high': True,
    'co2_emission_extra_high': True,
    'n_wheel_drive': True,
    'engine_is_turbo': True,
    'has_gear_box_thermal_management': True,
    'has_torque_converter': True,
    'fuel_saving_at_strategy': True,
    'engine_has_variable_valve_actuation': True,
    'has_thermal_management': True,
    'engine_has_direct_injection': True,
    'has_lean_burn': True,
    'engine_has_cylinder_deactivation': True,
    'active_cylinder_ratios': True,
    'has_exhausted_gas_recirculation': True,
    'has_periodically_regenerating_systems': True,
    'ki_additive': True,
    'ki_multiplicative': True,
    'has_particle_filter': True,
    'has_selective_catalytic_reduction': True,
    'has_nox_storage_catalyst': True,
    'n_dyno_axes': True,
    'times': True,
    'velocities': True,
    'obd_velocities': True,
    'bag_phases': True,
    'engine_speeds_out': True,
    'engine_coolant_temperatures': True,
    'co2_normalization_references': True,
    'service_battery_currents': True,
    'cycle_name': True,
    'cycle_type': True,
    'service_battery_nominal_voltage': True,
    'fuel_heating_value': True,
    'rcb_correction': True,
    'has_engine_idle_coasting': True,
    'has_engine_off_coasting': True,
}
calibration_conventional = {
    'has_start_stop': True,
    'has_energy_recuperation': True,
    'alternator_nominal_voltage': True,
    'alternator_nominal_power': True,
    'alternator_efficiency': True,
    'alternator_currents': True,
    'speed_distance_correction': True
}
calibration_hybrid = {
    'initial_drive_battery_state_of_charge': True,
    'planetary_ratio': True,
    'drive_battery_n_cells': True,
    'drive_battery_technology': True,
    'drive_battery_capacity': True,
    'motor_p0_maximum_power': True,
    'motor_p0_maximum_torque': True,
    'motor_p0_speed_ratio': True,
    'motor_p1_maximum_power': True,
    'motor_p1_maximum_torque': True,
    'motor_p1_speed_ratio': True,
    'motor_p2_maximum_power': True,
    'motor_p2_maximum_torque': True,
    'motor_p2_speed_ratio': True,
    'motor_p2_planetary_maximum_power': True,
    'motor_p2_planetary_maximum_torque': True,
    'motor_p2_planetary_speed_ratio': True,
    'motor_p3_front_maximum_power': True,
    'motor_p3_front_maximum_torque': True,
    'motor_p3_front_speed_ratio': True,
    'motor_p3_rear_maximum_power': True,
    'motor_p3_rear_maximum_torque': True,
    'motor_p3_rear_speed_ratio': True,
    'motor_p4_front_maximum_power': True,
    'motor_p4_front_maximum_torque': True,
    'motor_p4_front_speed_ratio': True,
    'motor_p4_rear_maximum_power': True,
    'motor_p4_rear_maximum_torque': True,
    'motor_p4_rear_speed_ratio': True,
    'drive_battery_voltages': True,
    'drive_battery_currents': True,
    'dcdc_converter_currents': True,
    'kco2_wltp_correction_factor': True
}

prediction = {
    'VERSION': True,
    'fuel_type': True,
    'engine_fuel_lower_heating_value': True,
    'fuel_carbon_content_percentage': True,
    'has_periodically_regenerating_systems': True,
    'has_gear_box_thermal_management': True,
    'ki_additive': True,
    'ki_multiplicative': True,
    'ignition_type': True,
    'engine_capacity': True,
    'engine_stroke': True,
    'engine_max_speed': True,
    'idle_engine_speed_median': True,
    'engine_idle_fuel_consumption': True,
    'final_drive_ratio': True,
    'final_drive_ratios': True,
    'tyre_code': True,
    'gear_box_type': True,
    'start_stop_activation_time': True,
    'service_battery_capacity': True,
    'gear_box_ratios': True,
    'full_load_speeds': True,
    'full_load_torques': True,
    'full_load_powers': True,
    'vehicle_mass': True,
    'f0': True,
    'f1': True,
    'f2': True,
    'engine_n_cylinders': True,
    'n_wheel_drive': True,
    'engine_is_turbo': True,
    'has_torque_converter': True,
    'fuel_saving_at_strategy': True,
    'engine_has_variable_valve_actuation': True,
    'has_thermal_management': True,
    'engine_has_direct_injection': True,
    'has_lean_burn': True,
    'engine_has_cylinder_deactivation': True,
    'active_cylinder_ratios': True,
    'has_exhausted_gas_recirculation': True,
    'has_particle_filter': True,
    'has_selective_catalytic_reduction': True,
    'has_nox_storage_catalyst': True,
    'times': True,
    'velocities': True,
    'gears': True,
    'bag_phases': True,
    'cycle_name': True,
    'cycle_type': True,
    'service_battery_nominal_voltage': True,
    'fuel_heating_value': True,
    'has_engine_idle_coasting': True,
    'has_engine_off_coasting': True,
}
prediction_conventional = {
    'has_start_stop': True,
    'has_energy_recuperation': True,
    'alternator_nominal_voltage': True,
    'alternator_nominal_power': True,
    'alternator_efficiency': True
}
prediction_hybrid = {
    'initial_drive_battery_state_of_charge': True,
    'planetary_ratio': True,
    'drive_battery_n_cells': True,
    'drive_battery_technology': True,
    'drive_battery_capacity': True,
    'motor_p0_maximum_power': True,
    'motor_p0_maximum_torque': True,
    'motor_p0_speed_ratio': True,
    'motor_p1_maximum_power': True,
    'motor_p1_maximum_torque': True,
    'motor_p1_speed_ratio': True,
    'motor_p2_maximum_power': True,
    'motor_p2_maximum_torque': True,
    'motor_p2_speed_ratio': True,
    'motor_p2_planetary_maximum_power': True,
    'motor_p2_planetary_maximum_torque': True,
    'motor_p2_planetary_speed_ratio': True,
    'motor_p3_front_maximum_power': True,
    'motor_p3_front_maximum_torque': True,
    'motor_p3_front_speed_ratio': True,
    'motor_p3_rear_maximum_power': True,
    'motor_p3_rear_maximum_torque': True,
    'motor_p3_rear_speed_ratio': True,
    'motor_p4_front_maximum_power': True,
    'motor_p4_front_maximum_torque': True,
    'motor_p4_front_speed_ratio': True,
    'motor_p4_rear_maximum_power': True,
    'motor_p4_rear_maximum_torque': True,
    'motor_p4_rear_speed_ratio': True,
    'kco2_nedc_correction_factor': True
}

#: Data to be parsed from the input when declaration mode is enabled.
DECLARATION_DATA = {
    None: {
        'target': True,
        'input': {
            'calibration': dict.fromkeys(('wltp_h', 'wltp_l'), calibration),
            'prediction': dict.fromkeys((
                'wltp_h', 'wltp_l', 'nedc_h', 'nedc_l'
            ), prediction)
        }
    },
    'conventional': {
        'input': {
            'calibration': dict.fromkeys((
                'wltp_h', 'wltp_l'
            ), calibration_conventional),
            'prediction': dict.fromkeys((
                'wltp_h', 'wltp_l', 'nedc_h', 'nedc_l'
            ), prediction_conventional)
        }
    },
    'hybrid': {
        'input': {
            'calibration': dict.fromkeys((
                'wltp_h', 'wltp_l'
            ), calibration_hybrid),
            'prediction': dict.fromkeys((
                'wltp_h', 'wltp_l', 'nedc_h', 'nedc_l'
            ), prediction_hybrid)
        }
    }
}


def _select_declaration_data(data, diff=None, is_hybrid=None):
    res = {}
    # noinspection PyTypeChecker
    keys = (None,) + {
        None: ('hybrid', 'conventional'),
        True: ('hybrid',),
        False: ('conventional',)
    }[is_hybrid]
    for i in keys:
        for k, v in sh.stack_nested_keys(DECLARATION_DATA[i]):
            if v and sh.are_in_nested_dicts(data, *k):
                v = sh.get_nested_dicts(data, *k)
                sh.get_nested_dicts(res, *k[:-1])[k[-1]] = v

    if diff is not None:
        diff.clear()
        diff.update(v[0] for v in sh.stack_nested_keys(data, depth=4))
        it = (v[0] for v in sh.stack_nested_keys(res, depth=4))
        diff.difference_update(it)
    return res


def _extract_declaration_data(inputs, errors, is_hybrid=None):
    diff = set()
    inputs = _select_declaration_data(inputs, diff, is_hybrid)
    errors = _select_declaration_data(errors, is_hybrid=is_hybrid)
    return inputs, errors, diff


def declaration_validation(
        type_approval_mode, inputs, errors, input_type=None,):
    """
    Parse input data for the declaration mode.

    :param type_approval_mode:
        Is launched for TA?
    :type type_approval_mode: bool

    :param inputs:
        Input data.
    :type inputs: dict

    :param errors:
        Errors container.
    :type errors: dict

    :param input_type:
        Type of file input.
    :type input_type: str

    :return:
        Parsed input data and errors container.
    :rtype: dict, dict
    """
    is_hybrid = input_type and input_type != 'Pure ICE'
    inputs, errors, diff = _extract_declaration_data(inputs, errors, is_hybrid)
    if diff:
        if type_approval_mode:
            msg = 'Cannot be used in type approval mode.'
            for k in diff:
                sh.get_nested_dicts(errors, *k[:-1])[k[-1]] = msg
        else:
            diff = ['.'.join(k) for k in sorted(diff)]
            log.info(
                'Since CO2MPAS is launched in declaration mode the '
                'following data are not used:\n %s\n'
                'If you want to execute it remove -DM from the cmd.',
                ',\n'.join(diff)
            )
    elif input_type == 'OVC-HEV':
        for k, v in sh.stack_nested_keys(inputs.get('input', {}), depth=2):
            v['is_plugin'] = True
    return inputs, errors
