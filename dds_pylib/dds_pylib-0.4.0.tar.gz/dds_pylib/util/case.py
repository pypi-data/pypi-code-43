''' Functions to convert string case

History:
05-05-2015 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'

import re


def camel_to_ashell_case(s):
    ''' convert camel case to A-Shell '''
    s1 = re.sub('(.)([A-Z][a-z]+)', r"\1'\2", s)
    return re.sub('([a-z0-9])([A-Z])', r"\1'\2", s1).lower()


def camel_to_snake_case(s):
    ''' convert camel case to snake case '''
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def snake_case_to_camel_case(s, upper_camel=True):
    ''' convert snake case to upper/lower camel case
    params:
        s - string to convert
        upper_camel - True convert to UpperCamelCase
                    - False convert to lowerCamelCase
    '''
    components = s.lower().split('_')
    if upper_camel:
        # We capitalize the first letter of each component with the
        # 'title' method and join them together.
        return ''.join(x.title() for x in components)
    else:
        # We capitalize the first letter of each component except the first one
        # with the 'title' method and join them together.
        return components[0] + ''.join(x.title() for x in components[1:])

def snake_case_to_ashell(s, upper=False):
    ''' convert snake case to A-Shell (default lower case)
    params:
        s - string to convert
        upper - True upper cases
    '''
    components = s.lower().split('_')
    # split on underscore and join with apostrophe
    ac = '\''.join(x for x in components)
    if upper:
        return ac.upper()
    return ac

def upcase_first_letter(s, lower=False):
    ''' upper case first letter of string '''
    if lower:
        s = s.lower()
    return s[0].upper() + s[1:]
