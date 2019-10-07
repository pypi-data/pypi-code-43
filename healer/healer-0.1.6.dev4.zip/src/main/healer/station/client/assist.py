"""
"""

import re

# __pragma__ ('skip')
this = None
window = None
document = None
# __pragma__ ('noskip')


class Assist:

    regex_v_single = re.compile(r'^v_([a-z]+)$')
    regex_v_double = re.compile(r'^v_([a-z]+)_([a-z_]+)$')

    @staticmethod
    def translate_attribute(attr_name:str):
        if attr_name == 'cls':
            return 'class'
        match = Assist.regex_v_single.match(attr_name)
        if match:
            return 'v-' + match.group(1)
        match = Assist.regex_v_double.match(attr_name)
        if match:
            return 'v-' + match.group(1) + ':' + match.group(2).replace('_', '-')
        return attr_name.replace('_', '-')

    @staticmethod
    def append_child(parent, child):
        if not child:
            pass
        elif isinstance(child, str):
            parent.textContent = child
        elif isinstance(child, list):
            for entry in child:
                parent.appendChild(entry)
        else:
            parent.appendChild(child)


def produce_tag(tag_name):

    # __pragma__ ('kwargs')
    def producer_fun(content=None, **attribute_dict):
        entry = document.createElement(tag_name)
        Assist.append_child(entry, content)
        for attrib_key, attrib_value in attribute_dict.items():
            attrib_name = Assist.translate_attribute(attrib_key)
            entry.setAttribute(attrib_name, attrib_value)
        return entry
    # __pragma__ ('nokwargs')

    return producer_fun

# __pragma__ ('noalias')


def name_of_fun(fun) -> str:
    "js function name"
    return fun.name


def name_of_tag(tag:"HTMLElement") -> str:
    "html element tag name"
    return tag().localName


def console_log(*args) -> None:
    window.console.log(*args)
