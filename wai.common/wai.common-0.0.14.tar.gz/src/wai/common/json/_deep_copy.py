from ._typing import RawJSONElement


def deep_copy(json: RawJSONElement) -> RawJSONElement:
    """
    Creates a deep-copy of the given raw JSON element.

    :param json:    The raw JSON element to copy.
    :return:        The copy.
    """
    if isinstance(json, dict):
        return {key: deep_copy(value) for key, value in json.items()}
    elif isinstance(json, list):
        return [deep_copy(array_element) for array_element in json]
    else:
        return json
