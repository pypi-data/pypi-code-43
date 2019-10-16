from index_by.modifier import index_by_modifier_as_list, index_by_modifier
from index_by.modifiers.pop_key import PopKeyModifier, PopKeysModifier


def index_by_pop_key(sequence, key_name, target_index=None):
    return index_by_modifier(
        sequence,
        PopKeyModifier(key_name),
        target_index)


def index_by_pop_key_as_list(sequence, key_name, target_index=None):
    return index_by_modifier_as_list(
        sequence,
        PopKeyModifier(key_name),
        target_index)


def index_by_pop_keys(sequence, key_names, target_index=None):
    return index_by_modifier(
        sequence,
        PopKeysModifier(key_names),
        target_index)


def index_by_pop_keys_as_list(sequence, key_names, target_index=None):
    return index_by_modifier_as_list(
        sequence,
        PopKeysModifier(key_names),
        target_index)
