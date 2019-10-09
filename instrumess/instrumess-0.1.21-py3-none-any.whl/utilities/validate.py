# -*- coding: utf-8 -*-
"""
Created on Wednesday 08-August-2018 at 11:17

@author: Rastko Pajković
"""


def in_set(value, set, name='Value'):
    """Chech if value is in a set, else raise ValueError
    
    Parameters
    ----------
    set : dict or list
        Check value against list elements or dict keys
    
    Returns
    -------
    TYPE
        value of set['value'] if set is a dict
    
    Raises
    ------
    ValueError
        Description
    """
    try:
        # turn dict keys to lowercase for comparison
        set = {name.lower(): val for name, val in set.items()}
        # if dict value should be string, turn to lowercase for comparison
        value = value.lower()
        allowed_values = set.keys()
        val = set.get(value)
    except AttributeError:
        # turn a list of strings into lowercase for comparison
        try:
            value = value.lower()
            set = [el.lower() for el in set]
        except:
            pass
        allowed_values = set
        val = value
    if value in set:
        return val
    else:
        print(value, set)
        raise ValueError("Allowed values for {} are {}".format(name,
                                                               allowed_values))


def in_range(value, range, name='Value'):
    """Check if min<=value<=max, else raise ValueError"""
    if not (min(range) <= value <= max(range)):
        raise ValueError('{} should be in '
                         '{}..{} range'.format(name, min(range), max(range)))
    return value
