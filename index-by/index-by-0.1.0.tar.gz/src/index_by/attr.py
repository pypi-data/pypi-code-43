from index_by.modifier import index_by_modifier_as_list, index_by_modifier
from index_by.modifiers.attr import AttributeModifier, AttributesModifier


def index_by_attr(sequence, attr_name, target_index=None):
    return index_by_modifier(
        sequence,
        AttributeModifier(attr_name),
        target_index)


def index_by_attr_as_list(sequence, attr_name, target_index=None):
    return index_by_modifier_as_list(
        sequence,
        AttributeModifier(attr_name),
        target_index)


def index_by_attrs(sequence, attr_names, target_index=None):
    return index_by_modifier(
        sequence,
        AttributesModifier(attr_names),
        target_index)


def index_by_attrs_as_list(sequence, attr_names, target_index=None):
    return index_by_modifier_as_list(
        sequence,
        AttributesModifier(attr_names),
        target_index)
