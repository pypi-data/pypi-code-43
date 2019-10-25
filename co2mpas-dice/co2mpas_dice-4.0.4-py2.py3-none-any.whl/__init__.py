# -*- coding: utf-8 -*-
#
# Copyright 2015-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
It provides CO2MPAS-TA output model.
"""

import io
import copy
import logging
import numpy as np
import os.path as osp
import schedula as sh

log = logging.getLogger(__name__)

dsp = sh.BlueDispatcher(name='DICE model')


@sh.add_function(dsp, outputs=['data2encrypt'])
def merge_data2encrypt(base, meta):
    """
    Merge and process data to encrypt.

    :param base:
        Base data.
    :type base: dict

    :param meta:
        Meta data.
    :type meta: dict

    :return:
        Data to encrypt.
    :rtype: tuple
    """
    data = {}
    for k, v in base.items():
        k = k.split('.')
        sh.get_nested_dicts(data, *k[:-1])[k[-1]] = v
    return data, meta


@sh.add_function(dsp, outputs=['encrypted_data'])
def encrypt_data(data2encrypt, encryption_keys):
    """
    Encrypt the data.

    :param data2encrypt:
        Data to encrypt.
    :type data2encrypt: tuple

    :param encryption_keys:
        Encryption keys for TA mode.
    :type encryption_keys: str

    :return:
        Encrypted data.
    :rtype: dict
    """
    from .crypto import encrypt_data as func
    return func(data2encrypt, encryption_keys)


def _get_nested(d, *keys):
    if keys:
        return _get_nested(d[keys[0]], *keys[1:])
    return d


def _stack(d, key=()):
    it = ()
    if hasattr(d, 'items'):
        it = d.items()
    elif isinstance(d, list):
        it = enumerate(d)
    else:
        yield key, d
    for k, v in it:
        yield from _stack(v, key=key + (k,))


@sh.add_function(dsp, outputs=['dice_report'])
def extract_dice_report(co2mpas_version, dice, start_time, report):
    """
    Extract DICE report.

    :param co2mpas_version:
        co2mpas version.
    :type co2mpas_version: str

    :param dice:
        DICE data.
    :type dice: dict

    :param start_time:
        Run start time.
    :type start_time: datetime.datetime

    :param report:
        Vehicle output report.
    :type report: dict

    :return:
        DICE report.
    :rtype: dict
    """
    res = {
        'info': {
            'vehicle_family_id': dice['vehicle_family_id'],
            'CO2MPAS_version': co2mpas_version,
            'datetime': start_time.strftime('%Y/%m/%d-%H:%M:%S')
        }
    }
    are_in, get_in = sh.are_in_nested_dicts, sh.get_nested_dicts
    # deviation
    keys = 'summary', 'comparison', 'prediction'
    if are_in(report, *keys):
        deviation = ['declared_co2_emission_value', 'prediction_target_ratio']
        if dice.get('input_type') == 'OVC-HEV':
            deviation[0] = 'declared_sustaining_co2_emission_value'
        for cycle, d in get_in(report, *keys).items():
            if are_in(d, *deviation):
                v = (get_in(d, *deviation) - 1) * 100
                get_in(res, 'deviation')[cycle] = v

    # gears
    keys = 'summary', 'comparison', 'calibration'
    if are_in(report, *keys):
        for cycle, d in get_in(report, *keys).items():
            if cycle.startswith('wltp_') and are_in(d, 'gears'):
                get_in(res, 'gears')[cycle] = get_in(d, 'gears')

    # vehicle
    keys = [('summary', 'results', 'vehicle'), ('prediction', 'output')]
    vehicle = (
        'fuel_type', 'engine_capacity', 'gear_box_type', 'engine_is_turbo',
        'engine_max_power', 'engine_speed_at_max_power',
        'service_battery_delta_state_of_charge',
        'drive_battery_delta_state_of_charge'
    )
    if are_in(report, *keys[0]):
        for cycle, d in get_in(report, *keys[0]).items():
            if are_in(d, *keys[1]):
                v = sh.selector(vehicle, get_in(d, *keys[1]), allow_miss=True)
                if v:
                    get_in(res, 'vehicle', cycle).update(v)

    # declared
    keys = [
        ('summary', 'results', 'declared_co2_emission'),
        ('prediction', 'target', 'declared_co2_emission_value')
    ]
    declared = {}
    if are_in(report, *keys[0]):
        for cycle, d in get_in(report, *keys[0]).items():
            if are_in(d, *keys[1]):
                declared[cycle] = get_in(d, *keys[1])

    for k in 'hl':
        i, j = 'wltp_%s' % k, 'nedc_%s' % k
        k = 'declared_wltp_%s_vs_declared_nedc_%s' % (k, k)
        if i in declared and j in declared:
            get_in(res, 'ratios')[k] = declared[i] / declared[j]

    # corrected
    keys = [
        ('summary', 'results', 'corrected_co2_emission'),
        ('prediction', 'target', 'corrected_co2_emission_value')
    ]
    corrected = {}
    if are_in(report, *keys[0]):
        for cycle, d in get_in(report, *keys[0]).items():
            if are_in(d, *keys[1]):
                corrected[cycle] = get_in(d, *keys[1])
    for k in 'hl':
        i = 'wltp_%s' % k
        k = 'declared_wltp_%s_vs_corrected_wltp_%s' % (k, k)
        if i in declared and i in corrected:
            get_in(res, 'ratios')[k] = declared[i] / corrected[i]

    # model scores
    keys = 'data', 'calibration', 'model_scores'
    model_scores = 'model_selections', 'param_selections', 'score_by_model', \
                   'scores'
    if are_in(report, *keys):
        get_in(res, 'model_scores').update(sh.selector(
            model_scores, get_in(report, *keys), allow_miss=True
        ))

    res = copy.deepcopy(res)
    for k, v in list(_stack(res)):
        if isinstance(v, np.generic):
            _get_nested(res, *k[:-1])[k[-1]] = v.item()

    return res


SKIP_PARAMETERS = ()


def _filter_data(report):
    from scipy.interpolate import InterpolatedUnivariateSpline as Spline
    report = {k: v for k, v in report.items() if k != 'pipe'}
    for k, v in sh.stack_nested_keys(report):
        if hasattr(v, '__call__') or hasattr(v, 'predict') or \
                (isinstance(v, list) and isinstance(v[0], Spline)) or \
                k[-1] in SKIP_PARAMETERS:
            continue
        yield '.'.join(map(str, k)), v


def _get_fuel(d):
    k = ('summary', 'results', 'vehicle', 'nedc_h', 'prediction', 'input',
         'fuel_type')
    return sh.are_in_nested_dicts(d, *k) and sh.get_nested_dicts(d, *k)


@sh.add_function(dsp, outputs=['ta_id'])
def define_ta_id(
        base, report, dice, meta, dice_report, encrypted_data, excel_output,
        excel_input, sign_key):
    """
    Defines TA data.

    :param base:
        Base data.
    :type base: dict

    :param report:
        Vehicle output report.
    :type report: dict

    :param dice:
        DICE data.
    :type dice: dict

    :param meta:
        Meta data.
    :type meta: dict

    :param dice_report:
        DICE report.
    :type dice_report: dict

    :param encrypted_data:
        Encrypted data.
    :type encrypted_data: dict

    :param excel_output:
        Excel output file.
    :type excel_output: io.BytesIO

    :param excel_input:
        Excel input file.
    :type excel_input: io.BytesIO

    :param sign_key:
        User signature key for TA mode.
    :type sign_key: str

    :return:
        TA data.
    :rtype: dict
    """
    import json
    import secrets
    from .crypto import sign_ta_id, make_hash, _json_default

    excel_output.seek(0)
    excel_input.seek(0)
    target = {k: v for k, v in base.items() if k.startswith('target.')}
    ta_id = {
        'vehicle_family_id': dice['vehicle_family_id'],
        'parent_vehicle_family_id': dice.get('parent_vehicle_family_id', ''),
        'hash': {
            'inputs': make_hash(json.dumps(
                base, default=_json_default, sort_keys=True
            ).encode()),
            'input': make_hash(json.dumps(
                {k: v for k, v in base.items() if k.startswith('input.')},
                default=_json_default, sort_keys=True
            ).encode()),
            'target_wltp': make_hash(json.dumps(
                {k: v for k, v in target.items() if 'wltp' in k},
                default=_json_default, sort_keys=True
            ).encode()),
            'target_nedc': make_hash(json.dumps(
                {k: v for k, v in target.items() if 'nedc' in k},
                default=_json_default, sort_keys=True
            ).encode()),
            'meta': make_hash(json.dumps(
                meta, default=_json_default, sort_keys=True
            ).encode()),
            'dice': make_hash(json.dumps(
                dice, default=_json_default, sort_keys=True
            ).encode()),
            'outputs': make_hash(json.dumps(
                dict(_filter_data(report)), default=_json_default,
                sort_keys=True
            ).encode()),
            'dice_report': make_hash(json.dumps(
                dice_report, default=_json_default, sort_keys=True
            ).encode()),
            'encrypted_data': make_hash(json.dumps(
                encrypted_data, default=_json_default, sort_keys=True
            ).encode()),
            'output_file': make_hash(excel_output.read()),
            'input_file': make_hash(excel_input.read()),
        },
        'user_random': secrets.randbelow(100),
        'extension': int(dice.get('extension', False)),
        'input_type': dice.get('input_type', 'Pure ICE'),
        'bifuel': int(dice.get('bifuel', False)),
        'wltp_retest': dice.get('wltp_retest', '-'),
        'comments': dice.get('comments', ''),
        'atct_family_correction_factor': dice.get(
            'atct_family_correction_factor', 1),
        'fuel_type': _get_fuel(report),
        'dice': dice
    }
    sign_ta_id(ta_id, sign_key)
    return ta_id


@sh.add_function(dsp, outputs=['dice'])
def get_dice_data(ta_id):
    """
    Return DICE data.

    :param ta_id:
        TA data.
    :type ta_id: dict

    :return:
        DICE data.
    :rtype: dict
    """
    return ta_id['dice']


def verify_ta_id(ta_id):
    """
    Verify TA data.

    :param ta_id:
        TA data.
    :type ta_id: dict

    :return:
        Verified TA data.
    :rtype: dict
    """
    import json
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import utils, padding
    from co2mpas_dice.crypto import _json_default, make_hash
    from co2mpas_dice.err import DiceError
    message = json.dumps(
        {k: v for k, v in ta_id.items() if k != 'signature'},
        default=_json_default, sort_keys=True
    ).encode()
    try:
        serialization.load_pem_public_key(
            ta_id['pub_sign_key'], default_backend()
        ).verify(
            ta_id['signature'], make_hash(message),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(hashes.SHA256())
        )
    except InvalidSignature:
        raise DiceError('Invalid signature of the ta report!')
    return ta_id


dsp.add_data('ta_id', filters=[verify_ta_id])


@sh.add_function(dsp, outputs=['output_file_name'])
def get_output_file_name(output_folder, timestamp, ta_id):
    """
    Returns the output file name.

    :param output_folder:
        Output folder.
    :type output_folder: str

    :param timestamp:
        Run timestamp.
    :type timestamp: str

    :param ta_id:
        TA data.
    :type ta_id: dict

    :return:
        Output file name.
    :rtype: str
    """
    i, _fpath = 0, osp.join(output_folder, '{}-%02d-{}.co2mpas.zip'.format(
        timestamp, ta_id['vehicle_family_id']
    ))

    while True:
        fpath = _fpath % i
        if not osp.isfile(fpath):
            return fpath
        i += 1


@sh.add_function(dsp, outputs=['output_file'])
def write_ta_file(
        output_file_name, ta_id, dice_report, encrypted_data, excel_output,
        excel_input):
    """
    Write correlation report file.

    :param output_file_name:
        Output file name.
    :type output_file_name: str

    :param ta_id:
        TA data.
    :type ta_id: dict

    :param dice_report:
        DICE report.
    :type dice_report: dict

    :param encrypted_data:
        Encrypted data.
    :type encrypted_data: dict

    :param excel_output:
        Excel output file.
    :type excel_output: io.BytesIO

    :param excel_input:
        Excel input file.
    :type excel_input: io.BytesIO

    :return:
        Correlation report file.
    :rtype: io.BytesIO
    """

    import json
    import zipfile
    from .tar import save_data
    from .crypto import make_hash, _json_default
    kw = dict(
        ta_id=ta_id, dice_report=dice_report, encrypted_data=encrypted_data
    )
    ta_hash = make_hash(json.dumps(
        kw, default=_json_default, sort_keys=True
    ).encode()).hex()
    name = osp.splitext(osp.basename(output_file_name))[0]

    file = io.BytesIO()
    with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zf:
        excel_input.seek(0)
        zf.writestr('%s.input.xlsx' % name, excel_input.read())
        excel_output.seek(0)
        zf.writestr('%s.output.xlsx' % name, excel_output.read())

        ta_file = save_data(io.BytesIO(), **kw)
        ta_file.seek(0)
        zf.writestr('%s.ta' % name, ta_file.read())
        zf.writestr('%s.hash.txt' % name, ta_hash)
    log.info('Hash of correlation-report: %s.' % ta_hash)
    return file


@sh.add_function(
    dsp, outputs=['ta_id', 'dice_report', 'encrypted_data', 'data']
)
def load_data(input_file):
    """
    Loads data from TA file.

    :param input_file:
        Input file.
    :type input_file: io.BytesIO

    :return:
        Data of TA file.
    :rtype: list[dict]
    """
    from .tar import load_data as func
    input_file.seek(0)
    data = func(input_file)
    data['encrypted_data'] = data.get('encrypted_data', sh.NONE)
    data['data'] = data.get('data', sh.NONE)
    return sh.selector(
        ('ta_id', 'dice_report', 'encrypted_data', 'data'), data,
        output_type='list'
    )


@sh.add_function(
    dsp, inputs_kwargs=True, inputs_defaults=True, outputs=['data2encrypt']
)
def decrypt_data(
        encrypted_data, encryption_keys, encryption_keys_passwords=None):
    """
    Encrypt the data.

    :param encrypted_data:
        Encrypted data.
    :type encrypted_data: dict

    :param encryption_keys:
        Encryption keys for TA mode.
    :type encryption_keys: str

    :param encryption_keys_passwords:
        Encryption keys passwords.
    :type encryption_keys_passwords: str

    :return:
        Data to encrypt.
    :rtype: tuple
    """
    import json
    from .crypto import decrypt_data as func
    passwords = None
    if encryption_keys_passwords:
        with open(encryption_keys_passwords) as f:
            passwords = {k: v.encode() for k, v in json.load(f).items()}

    return func(encrypted_data, encryption_keys, passwords)


dsp.add_function(
    function_id='split_data2encrypt',
    function=sh.bypass,
    inputs=['data2encrypt'],
    outputs=['base', 'meta']
)
