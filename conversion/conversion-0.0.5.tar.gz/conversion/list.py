def convert_list(value: str, delimeter=",", raise_exception=True) -> list:
    converted = value

    try:
        converted = [x.strip() for x in value.split(delimeter)]
    except Exception as exc:
        if raise_exception:
            raise

    return converted
