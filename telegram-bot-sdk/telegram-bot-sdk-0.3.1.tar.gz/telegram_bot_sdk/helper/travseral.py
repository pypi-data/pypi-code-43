def replace_keys_from_dict(old_key, new_key, dict_to_use):
    return _replace_keys_from_dict(old_key, new_key, dict_to_use)


def _replace_keys_from_dict(old_key, new_key, layer):

    if isinstance(layer, list):
        for items in layer:
            _replace_keys_from_dict(old_key, new_key, items)

    elif isinstance(layer, dict):
        to_delete = []

        for key in layer:
            if key == old_key:
                to_delete.append(key)
            _replace_keys_from_dict(old_key, new_key, layer[key])

        for key in to_delete:
            layer[new_key] = layer[old_key]
            del layer[key]

    return layer
