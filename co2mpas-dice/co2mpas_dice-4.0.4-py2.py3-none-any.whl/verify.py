import logging
import functools
import os.path as osp
import schedula as sh

log = logging.getLogger(__name__)


def _cycle_condition(data, k):
    return sh.are_in_nested_dicts(data, *(k[:-1] + ('vehicle_mass',)))


def _extend_checks(base, *extras):
    base = {k: list(v) for k, v in base.items()}
    for extra in extras:
        for k, v in extra.items():
            if isinstance(v, list):
                sh.get_nested_dicts(base, k, default=list).extend(v)
            else:
                sh.get_nested_dicts(base, k, default=list).append(v)
    return base


def _get(d, k):
    return sh.are_in_nested_dicts(d, *k) and sh.get_nested_dicts(d, *k)


def _fuel_saving_at_strategy(d, k):
    return _get(d, k[:-1] + ('gear_box_type',)) == 'automatic'


def _gear_box_ratios(d, k):
    return _get(d, k[:-1] + ('gear_box_type',)) in ('automatic', 'manual')


def _active_cylinder_ratios(d, k):
    return _get(d, k[:-1] + ('engine_has_cylinder_deactivation',))


def _ki_multiplicative(d, k):
    if _get(d, k[:-1] + ('has_periodically_regenerating_systems',)):
        return not sh.are_in_nested_dicts(d, *(k[:-1] + ('ki_additive',)))


def _ki_additive(d, k):
    if _get(d, k[:-1] + ('has_periodically_regenerating_systems',)):
        return not sh.are_in_nested_dicts(d, *(k[:-1] + ('ki_multiplicative',)))


def _final_drive_ratio(d, k):
    return not sh.are_in_nested_dicts(d, *(k[:-1] + ('final_drive_ratios',)))


def _final_drive_ratios(d, k):
    return not sh.are_in_nested_dicts(d, *(k[:-1] + ('final_drive_ratio',)))


def _start_stop_activation_time(d, k):
    return _get(d, k[:-1] + ('has_start_stop',))


def _target_gears(d, k):
    return _get(d, k[:-1] + ('gear_box_type',)) == 'manual'


def _planetary_ratio(d, k):
    return _get(d, k[:-1] + ('gear_box_type',)) == 'planetary'


# noinspection PyUnusedLocal
def _is_hybrid(d, k):
    v = _get(d, ('dice', 'input_type'))
    return v and v != "Pure ICE"


# noinspection PyUnusedLocal
def _is_plugin(d, k):
    return _get(d, ('dice', 'input_type')) == 'OVC-HEV'


def _is_not_hybrid(d, k):
    return not _is_hybrid(d, k)


def _is_not_plugin(d, k):
    return not _is_plugin(d, k)


def __motor_px(x):
    keys = (
        'motor_p%s_speed_ratio' % x, 'motor_p%s_maximum_torque' % x,
        'motor_p%s_maximum_power' % x
    )

    def _motor_px(d, k):
        return any(_get(d, k[:-1] + (i,)) for i in keys)

    return dict.fromkeys(keys, _motor_px)


_base = _extend_checks(
    {},
    dict.fromkeys((
        'has_periodically_regenerating_systems', 'engine_idle_fuel_consumption',
        'engine_has_variable_valve_actuation', 'fuel_carbon_content_percentage',
        'has_selective_catalytic_reduction', 'engine_has_cylinder_deactivation',
        'start_stop_activation_time', 'alternator_nominal_voltage', 'fuel_type',
        'service_battery_nominal_voltage', 'fuel_heating_value', 'vehicle_mass',
        'has_exhausted_gas_recirculation', 'final_drive_ratio', 'engine_stroke',
        'engine_fuel_lower_heating_value', 'alternator_efficiency', 'tyre_code',
        'fuel_saving_at_strategy', 'has_torque_converter', 'engine_n_cylinders',
        'service_battery_capacity', 'active_cylinder_ratios', 'engine_capacity',
        'idle_engine_speed_median', 'alternator_nominal_power', 'gear_box_type',
        'has_gear_box_thermal_management', 'engine_is_turbo', 'gear_box_ratios',
        'final_drive_ratios', 'n_wheel_drive', 'ignition_type', 'has_lean_burn',
        'has_engine_off_coasting', 'full_load_powers', 'full_load_speeds', 'f0',
        'f1', 'f2', 'has_engine_idle_coasting',
    ), _cycle_condition),
    {
        'final_drive_ratio': _final_drive_ratio,
        'final_drive_ratios': _final_drive_ratios,
        'start_stop_activation_time': _start_stop_activation_time,
        'fuel_saving_at_strategy': _fuel_saving_at_strategy,
        'active_cylinder_ratios': _active_cylinder_ratios,
        'gear_box_ratios': _gear_box_ratios,
    },
    dict.fromkeys((
        'has_start_stop', 'has_energy_recuperation', 'alternator_nominal_power',
        'alternator_nominal_voltage', 'alternator_efficiency'), _is_not_hybrid
    ),
    dict.fromkeys((
        'drive_battery_n_cells',
        'drive_battery_technology', 'drive_battery_capacity'), _is_hybrid
    ),
    dict.fromkeys((
        'motor_p2_planetary_speed_ratio', 'motor_p2_planetary_maximum_torque',
        'planetary_ratio', 'motor_p2_planetary_maximum_power'), _planetary_ratio
    ),
    __motor_px('0'), __motor_px('1'), __motor_px('2'), __motor_px('3_front'),
    __motor_px('3_rear'), __motor_px('4_front'), __motor_px('4_rear'),
)

_nedc = _extend_checks(
    _base,
    dict.fromkeys(('ki_multiplicative', 'ki_additive'), _cycle_condition),
    {
        'ki_multiplicative': _ki_multiplicative,
        'ki_additive': _ki_additive
    },
    dict.fromkeys(('kco2_nedc_correction_factor',), _is_hybrid),
)

_wltp = _extend_checks(_base, dict.fromkeys((
    'engine_coolant_temperatures', 'service_battery_currents', 'obd_velocities',
    'initial_drive_battery_state_of_charge', 'engine_speeds_out', 'n_dyno_axes',
    'co2_normalization_references', 'dcdc_converter_currents', 'rcb_correction',
    'speed_distance_correction', 'co2_emission_extra_high', 'co2_emission_high',
    'drive_battery_voltages', 'drive_battery_currents', 'co2_emission_medium',
    'alternator_currents', 'initial_temperature', 'co2_emission_low', 'times',
    'velocities', 'kco2_wltp_correction_factor'
), _cycle_condition), dict.fromkeys((
    'alternator_currents', 'speed_distance_correction'
), _is_not_hybrid), dict.fromkeys((
    'initial_drive_battery_state_of_charge', 'kco2_wltp_correction_factor',
    'drive_battery_voltages', 'drive_battery_currents',
    'dcdc_converter_currents',
), _is_hybrid))


# noinspection PyUnusedLocal
def _rel_cycle_cond(d, k, stage='calibration', cycle='wltp_l'):
    keys = 'base', 'input', stage, cycle, 'vehicle_mass'
    return sh.are_in_nested_dicts(d, *keys)


# noinspection PyUnusedLocal
def _mandatory(*a):
    return True


(dict.fromkeys((
    'alternator_currents',
), _is_not_hybrid), dict.fromkeys((
    'drive_battery_voltages', 'drive_battery_currents',
    'dcdc_converter_currents',
), _is_hybrid)
)


def _meta_mandatory(d, k):
    for i in ('', '.10hz', '.target'):
        if sh.are_in_nested_dicts(d, *(k[:-2] + (k[-2] + i,))):
            return True


_meta = _extend_checks(
    dict.fromkeys((
        'times', 'velocities', 'obd_velocities', 'engine_speeds_out',
        'engine_coolant_temperatures', 'co2_normalization_references',
        'alternator_currents', 'service_battery_currents', 'co2_emission_low',
        'co2_emission_medium', 'co2_emission_high', 'co2_emission_extra_high',
        'rcb_correction', 'speed_distance_correction',), [_meta_mandatory]),
    dict.fromkeys((
        'drive_battery_voltages', 'drive_battery_currents',
        'dcdc_converter_currents',
    ), [_meta_mandatory, _is_plugin]),
    dict.fromkeys((
        'alternator_currents', 'co2_emission_low',
        'co2_emission_medium', 'co2_emission_high', 'co2_emission_extra_high',
        'rcb_correction', 'speed_distance_correction'), [_is_not_hybrid]
    )
)


def _meta_plugin(d, k):
    return _is_plugin(d, k) or _meta_mandatory(d, k)


_co2_nedc = 'declared_co2_emission_value',
_co2_wltp = 'declared_co2_emission_value', 'corrected_co2_emission_value'
_co2_no_plugin_wltp = 'fuel_consumption_value',
_co2_plugin_nedc = (
    'nedc_electric_range',
    'declared_depleting_co2_emission_value',
    'declared_sustaining_co2_emission_value',
)
_co2_plugin_wltp = (
    'wltp_electric_range',
    'transition_cycle_index',
    'depleting_co2_emission_value',
    'relative_electric_energy_change',
    'sustaining_fuel_consumption_value',
    'declared_sustaining_co2_emission_value',
    'corrected_sustaining_co2_emission_value',
)

MANDATORY = {
    'flag': {
        'input_version': [_mandatory],
        'sign_key': [_mandatory],
        'encryption_keys': [_mandatory],

    },
    'dice': {
        'vehicle_family_id': [_mandatory],
        'bifuel': [_mandatory],
        'extension': [_mandatory],
        'atct_family_correction_factor': [_mandatory],
        'incomplete': [_mandatory],
        'regulation': [_mandatory],
        'input_type': [_mandatory],
        'wltp_retest': [_mandatory],

    },
    'base': {
        'target.calibration.wltp_h': {
            'gears': [_mandatory, _target_gears],
        },
        'target.calibration.wltp_l': {
            'gears': [_rel_cycle_cond, _target_gears],
        },
        'target.prediction.nedc_h': sh.combine_dicts(
            dict.fromkeys(_co2_nedc, [_mandatory]),
            dict.fromkeys(_co2_plugin_nedc, [_mandatory, _is_plugin])
        ),
        'target.prediction.nedc_l': sh.combine_dicts(
            dict.fromkeys(_co2_nedc, [functools.partial(
                _rel_cycle_cond, stage='prediction', cycle='nedc_l'
            )]),
            dict.fromkeys(_co2_plugin_nedc, [functools.partial(
                _rel_cycle_cond, stage='prediction', cycle='nedc_l'
            ), _is_plugin])
        ),
        'target.prediction.wltp_h': sh.combine_dicts(
            dict.fromkeys(_co2_wltp, [_mandatory]),
            dict.fromkeys(_co2_no_plugin_wltp, [_mandatory, _is_not_plugin]),
            dict.fromkeys((_co2_plugin_wltp), [_mandatory, _is_plugin])
        ),
        'target.prediction.wltp_l': sh.combine_dicts(
            dict.fromkeys(_co2_wltp, [_rel_cycle_cond]),
            dict.fromkeys(_co2_no_plugin_wltp,
                          [_rel_cycle_cond, _is_not_plugin]),
            dict.fromkeys((_co2_plugin_wltp), [_rel_cycle_cond, _is_plugin])
        ),
        'input.calibration.wltp_l': _wltp,
        'input.calibration.wltp_h': sh.combine_dicts(
            _wltp, {'vehicle_mass': [_mandatory]}
        ),
        'input.prediction.nedc_l': _nedc,
        'input.prediction.nedc_h': sh.combine_dicts(
            _nedc, {'vehicle_mass': [_mandatory]}
        )
    },
    'meta': {
        'wltp_h.10hz': dict.fromkeys(('times', 'velocities'), [_mandatory]),
        'wltp_l.10hz': dict.fromkeys(('times', 'velocities'),
                                     [_rel_cycle_cond]),
        'wltp_h.test_b': sh.combine_dicts(_meta, {'times': [_meta_plugin]}),
        'wltp_h.test_b.target': dict.fromkeys(
            ('fuel_consumption_value', 'corrected_co2_emission_value'),
            [_meta_mandatory]
        ),
        'wltp_h.test_b.10hz': dict.fromkeys(
            ('times', 'velocities'), [_meta_mandatory]
        ),
        'wltp_l.test_b': _meta,
        'wltp_l.test_b.target': dict.fromkeys(
            ('fuel_consumption_value', 'corrected_co2_emission_value'),
            [_meta_mandatory]
        ),
        'wltp_l.test_b.10hz': dict.fromkeys(
            ('times', 'velocities'), [_meta_mandatory]
        ),
        'wltp_h.test_c': _meta,
        'wltp_h.test_c.target': dict.fromkeys(
            ('fuel_consumption_value', 'corrected_co2_emission_value'),
            [_meta_mandatory]
        ),
        'wltp_h.test_c.10hz': dict.fromkeys(
            ('times', 'velocities'), [_meta_mandatory]
        ),
        'wltp_l.test_c': _meta,
        'wltp_l.test_c.target': dict.fromkeys(
            ('fuel_consumption_value', 'corrected_co2_emission_value'),
            [_meta_mandatory]
        ),
        'wltp_l.test_c.10hz': dict.fromkeys(
            ('times', 'velocities'), [_meta_mandatory]
        ),
    }
}


def _check_mandatory_inputs(data):
    err = []
    for k, funcs in sh.stack_nested_keys(MANDATORY):
        if all(f(data, k) for f in funcs):
            not sh.are_in_nested_dicts(data, *k) and err.append(k)

    return err


def _check_fuel(base, data_id='fuel_type'):
    d = base.get('input', {})
    fuels = {
        sh.get_nested_dicts(d, *(k + (data_id,)))
        for k in (('calibration', 'wlpt_h'), ('calibration', 'wlpt_l'),
                  ('prediction', 'nedc_h'), ('prediction', 'nedc_l'))
        if sh.are_in_nested_dicts(d, *(k + (data_id,)))
    }

    return len(fuels) > 1


def _check_encryption_keys(encryption_keys):
    if osp.isfile(encryption_keys):
        from .crypto import load_RSA_keys
        keys = load_RSA_keys(encryption_keys).get('public', {})
        return set(keys) - {'secret', 'server'}
    return True


def _check_sign_key(sign_key):
    from .crypto import load_sign_key
    try:
        load_sign_key(sign_key)
    except Exception:
        return True
    return not osp.isfile(sign_key)


def verify_flag(flag):
    """
    Validate flags for declaration-mode.

    :param flag:
        Flags data.
    :type flag: dict

    :return:
        If flags are valid.
    :rtype: bool
    """
    b, errors = False, [
        'flag.%s: Cannot be used.' % k
        for k in ('model_conf', 'enable_selector') if flag.get(k)
    ]
    from co2mpas.defaults import dfl
    if dfl:
        errors.append('physical model defaults: Cannot be modified.')

    for k in ('type_approval_mode', 'declaration_mode', 'hard_validation'):
        if flag.get(k):
            b = True
        elif b:
            errors.append('flag.%s: Cannot be false.' % k)
    if not errors:
        return True

    log.info(
        'Since CO2MPAS is launched in %s mode:\n %s\n'
        'If you want to execute it remove -DM or -TA from the cmd.',
        flag.get('type_approval_mode') and 'type approval' or 'declaration',
        ',\n'.join(errors)
    )
    return False


def validate_dice(dice=None):
    """
    Validate DICE data.

    :param dice:
        DICE data.
    :type dice: dict

    :return:
        Validated DICE data.
    :rtype: dict
    """
    from .schema import define_dice_schema
    from co2mpas.core.load.validate import _add_validated_input, _log_errors_msg
    inputs, errors, validate = {}, {}, define_dice_schema().validate
    for k, v in sorted((dice or {}).items()):
        _add_validated_input(inputs, validate, ('dice', k), v, errors)

    if inputs.get('extension') and inputs.get('wltp_retest', '-') != '-':
        sh.get_nested_dicts(errors, 'dice')['extension'] = (
            "Invalid combination `dice.extension == True` and "
            "`dice.wltp_retest != '-'`. Please set `dice.extension = False` "
            "or set `dice.wltp_retest = '-'`!"
        )

    if _log_errors_msg(errors):
        return sh.NONE
    return inputs


def _check_gear_box(data):
    from co2mpas.core.load.validate.hard import _check_gear_box

    res = _check_gear_box(dict(
        is_hybrid=data['dice']['input_type'] != 'Pure ICE',
        gear_box_type=data['base']['input.calibration.wltp_h']['gear_box_type']
    ))
    if res:
        log.info(res[1])
        return True


def verify_data(data):
    """
    Validate data for ta-mode.

    :param data:
        Data to validate.
    :type data: dict

    :return:
        If data are valid.
    :rtype: bool
    """
    missing = _check_mandatory_inputs(data)
    if missing:
        log.info('Since CO2MPAS is launched in type approval mode the '
                 'following data are mandatory:\n %s\n'
                 'If you want to run without it use the cmd batch.',
                 ',\n'.join(map('.'.join, missing)))
        return False

    if _check_gear_box(data):
        return False

    if _check_fuel(data):
        log.info('Since CO2MPAS is launched in type approval mode only one '
                 'type of fuel can be used.\nIf you want to simulate with '
                 'different fuels use the cmd batch.')
        return False

    if _check_encryption_keys(data['flag']['encryption_keys']):
        log.info('Since CO2MPAS is launched in type approval mode the '
                 'encryption keys are mandatory.\nPlease download it and add '
                 'in the dice keys folder.')
        return False

    if _check_sign_key(data['flag']['sign_key']):
        log.info('Since CO2MPAS is launched in type approval mode the '
                 'sign key is mandatory.\nPlease add in the dice keys folder '
                 'and specify the right password.')
        return False

    return True
