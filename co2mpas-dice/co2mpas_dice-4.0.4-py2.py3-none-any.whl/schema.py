import functools
import schedula as sh


@functools.lru_cache(None)
def define_dice_schema(read=True):
    """
    Define DICE schema.

    :param read:
        Schema for reading?
    :type read: bool

    :return:
        DICE schema.
    :rtype: schema.Schema
    """
    from schema import Or, And, Use, Optional, Schema
    from co2mpas.core.load.schema import (
        _string, _type, _vehicle_family_id, _compare_str, _select, Empty
    )
    string = _string(read=read)
    _bool = _type(type=bool, read=read)
    _float = _type(type=float, read=read)
    schema = {
        _compare_str('vehicle_family_id'): _vehicle_family_id(read=read),
        _compare_str('bifuel'): _bool,
        _compare_str('extension'): _bool,
        _compare_str('incomplete'): _bool,
        _compare_str('regulation'): string,
        _compare_str('comments'): string,
        _compare_str('atct_family_correction_factor'): _float,
        _compare_str('wltp_retest'): _select(
            types=('-', 'a', 'b', 'c', 'd', 'ab', 'ac', 'ad', 'bc', 'bd', 'cd',
                   'abc', 'abd', 'abcd'), read=read),
        _compare_str('parent_vehicle_family_id'): _vehicle_family_id(read=read),
        _compare_str('input_type'): _select(types=(
            'Pure ICE', 'NOVC-HEV', 'OVC-HEV'
        ), read=read),
        str: Or(Use(float), object)
    }

    schema = {Optional(k): Or(Empty(), v) for k, v in schema.items()}

    if not read:
        def _f(x):
            return x is sh.NONE

        schema = {k: And(v, Or(_f, Use(str))) for k, v in schema.items()}

    return Schema(schema)
