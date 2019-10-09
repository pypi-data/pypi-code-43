def convert_list(value: str, delimiter=",", raise_exception=True) -> list:
    converted = value

    if not value:
        return []

    try:
        converted = [x.strip() for x in value.split(delimiter)]
    except Exception as exc:
        if raise_exception:
            raise

    return converted
