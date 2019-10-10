def safe_cast(value, to_type, default=None):
    """Cast a value to another type safely.

    :param value: The original value.
    :param type to_type: The destination type.
    :param default: The default value.
    """
    try:
        return to_type(value)
    except (ValueError, TypeError):
        return default
