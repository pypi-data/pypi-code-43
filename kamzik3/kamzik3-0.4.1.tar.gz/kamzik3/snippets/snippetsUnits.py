import datetime
import math

from pint import UndefinedUnitError

from kamzik3 import units
from kamzik3.constants import *


def _base_unit(unit):
    try:
        prefix, base_unit, suffix = next(units.parse_unit_name(unit))
    except (UndefinedUnitError, AttributeError, StopIteration):
        prefix, base_unit, suffix = None, unit, None
    return prefix, base_unit, suffix


def get_attribute_unit_range(attribute):
    prefix, base_unit, suffix = _base_unit(attribute[UNIT])

    if base_unit in ("ampere", "volt", "meter", "degree", "radian", "second", "hertz", "percent"):
        sorted_prefixes = (
            'y', 'z', 'a', 'f', 'p', 'n', 'u', 'm', "", 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'
        )
    elif base_unit in ("degC", "degF", "K"):
        return ["degC", "degF", "K"]
    elif base_unit in ("bar", "Pa", "atm"):
        return ["mbar", "bar", "Pa", "kPa", "atm"]
    else:
        sorted_prefixes = (
            'y', 'z', 'a', 'f', 'p', 'n', 'u', 'm', 'c', 'd', "", 'da', 'h', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y'
        )
    try:
        converter = units._prefixes[prefix]._converter
        if converter == 1:
            scale = 1
        else:
            scale = converter.scale
    except KeyError:
        scale = 1

    try:
        min_unit = scale * 10 ** -attribute[DECIMALS]
        max_unit = scale * abs(attribute[MAX])
    except TypeError:
        raise TypeError

    unit_range = []
    for prefix in sorted_prefixes:
        converter = units._prefixes[prefix]._converter
        if converter == 1:
            scale = 1
        else:
            scale = converter.scale
        if min_unit <= scale <= max_unit:
            unit_range.append(units.get_symbol("{}{}".format(prefix, base_unit)))

    return unit_range


def get_decimals_diff(old_unit, new_unit):
    old_scale = math.log(units.get_base_units(old_unit)[0], 10)
    new_scale = math.log(units.get_base_units(new_unit)[0], 10)
    return int(round(old_scale - new_scale))


def device_units(device, attribute, value):
    try:
        value = value.replace("%", "percent")
    except AttributeError:
        pass

    device_unit = device.get_attribute(attribute)[UNIT]
    # try:
    converted_value = units.Quantity(value)
    # No unit for value
    if converted_value.unitless:
        # Return in value in device units
        try:
            return units.Quantity(float(units.Quantity(value, device_unit).m), device_unit)
        except AttributeError:
            return units.Quantity(float(units.Quantity(value).m))
    else:
        # Return converted value
        return converted_value.to(device_unit)
    # except DimensionalityError:
    #     # Values are not convertable among each other
    #     return units.Quantity(value, device_unit)


MAX_SECONDS = 2 ** 31 - 1


def get_scaled_time_duration(seconds):
    if seconds < 0: return
    if seconds > MAX_SECONDS:
        seconds = MAX_SECONDS

    d = datetime.datetime(1, 1, 1) + datetime.timedelta(seconds=seconds)

    if seconds < 60:
        milliseconds = int(d.microsecond / 1000)
        if milliseconds > 0:
            time_estimate = "{} Sec {} MSec".format(d.second, milliseconds)
        else:
            time_estimate = "{} Sec".format(d.second)
    elif 60 <= seconds < 3600:
        time_estimate = "{} Min {} Sec".format(d.minute, d.second)
    elif 3600 <= seconds < 24 * 3600:
        time_estimate = "{} Hour {} Min".format(d.hour, d.minute)
    elif 24 * 3600 <= seconds < 24 * 3600 * 28:
        time_estimate = "{} Day {} Hour {} Min".format(d.day - 1, d.hour, d.minute)
    elif 24 * 3600 * 28 <= seconds < 24 * 3600 * 28 * 12:
        time_estimate = "{} Month {} Day {} Hour".format(d.month, d.day - 1, d.hour)
    else:
        time_estimate = "{} Year {} Month {} Day".format(d.year, d.month, d.day - 1)

    return time_estimate


def seconds_to_datetime(seconds):
    if seconds > MAX_SECONDS:
        seconds = MAX_SECONDS

    return datetime.datetime.fromtimestamp(seconds).strftime("%d.%m.%Y %H:%M:%S")
