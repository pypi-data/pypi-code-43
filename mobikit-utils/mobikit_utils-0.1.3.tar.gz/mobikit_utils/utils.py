#
# Copyright (c) 2019 Mobikit, Inc.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

def check_keys(data, required_keys):
    """Return the keys that are missing from the data dictionary."""
    extra_keys = []
    required_keys = set(required_keys)
    for key in data.keys():
        if key not in required_keys:
            extra_keys.append(key)
        else:
            required_keys.remove(key)
    missing_keys = list(required_keys)
    return missing_keys, extra_keys


def clean_keys(data, extra_keys):
    """Remove extraneous keys from a dictionary."""
    data = {**data}
    for key in extra_keys:
        del data[key]
    return data


def raise_for_values(data, key, allowed_values=[], ExceptionClass=ValueError):
    if data[key] not in allowed_values:
        actual_val = str(data[key])
        val_str = ", ".join([str(allowed_value) for allowed_value in allowed_values])
        raise ExceptionClass(
            f"Expected {key} to be one of the following values: ({val_str}). Got {actual_val} instead"
        )
    return data


def raise_for_types(data, key, allowed_types=[], ExceptionClass=ValueError):
    if not any([isinstance(data[key], allowed_type) for allowed_type in allowed_types]):
        actual_type = str(type(data[key]))
        type_str = ", ".join([str(allowed_type) for allowed_type in allowed_types])
        raise ExceptionClass(
            f"Expected {key} to be one of the following types: ({type_str}). Got {actual_type} instead"
        )
    return data


def raise_for_keys(data, required_keys, clean=False, ExceptionClass=ValueError):
    """Raise an exception if required keys are missing, otherwise return cleaned data"""
    missing_keys, extra_keys = check_keys(data, required_keys)
    if missing_keys:
        key_str = ", ".join(missing_keys)
        raise ExceptionClass(f"Missing required keys {key_str}")
    if clean:
        data = clean_keys(data, extra_keys)
    return data


def trigger_sentry_error(request):
    division_by_zero = 1 / 0
