def index_by_modifier(sequence, modifier, target_index=None):
    """
    Create an index of objects in a sequence. The index's key will be provider by the modifier. Values are single
    objects, so in case of a duplicate key the latest object will persist.

    The modifier is called for each object with that object as an argument and is supposed to
    return the key to be used for that object in the index.

    :param sequence: sequence of objects (list, tuple or otherwise iterable object)
    :param modifier: callable that takes an object and returns a hashable value.
    :param target_index: dict that will be populated with objects from the sequence (optional)
    :return: dict
    """
    index = target_index if target_index is not None else dict()
    for element in sequence:
        key = modifier(element)
        index[key] = element
    return index


def index_by_modifier_as_list(sequence, modifier, target_index=None):
    """
    Create an index of objects in a sequence. The index's key will be provider by the modifier. Values are lists,
    so keys are not expected to be unique.

    The modifier is called for each object with that object as an argument and is supposed to
    return the key to be used for that object in the index.

    :param sequence: sequence of objects (list, tuple or otherwise iterable object)
    :param modifier: callable that takes an object and returns a hashable value.
    :param target_index: dict that will be populated with objects from the sequence (optional)
    :return: dict
    """
    index = target_index if target_index is not None else dict()
    for element in sequence:
        key = modifier(element)
        index.setdefault(key, [])
        index[key].append(element)
    return index
