from index_by.modifier import index_by_modifier_as_list, index_by_modifier
from index_by.modifiers.key import KeyModifier, KeysModifier


def index_by_key(sequence, key_name, target_index=None):
    return index_by_modifier(
        sequence,
        KeyModifier(key_name),
        target_index)


def index_by_key_as_list(sequence, key_name, target_index=None):
    return index_by_modifier_as_list(
        sequence,
        KeyModifier(key_name),
        target_index)


def index_by_keys(sequence, key_names, target_index=None):
    return index_by_modifier(
        sequence,
        KeysModifier(key_names),
        target_index)


def index_by_keys_as_list(sequence, key_names, target_index=None):
    return index_by_modifier_as_list(
        sequence,
        KeysModifier(key_names),
        target_index)
