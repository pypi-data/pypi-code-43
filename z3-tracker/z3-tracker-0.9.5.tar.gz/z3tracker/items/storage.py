'''
Item/dungeon tracker saving
'''

import json
import os.path

from ..config import CONFIG, CONFIGDIRECTORY
from ..version import __version__ as version

__all__ = (
    'load_items', 'load_dungeons', 'load_locations', 'load_entrances'
    'store_items', 'store_dungeons', 'store_locations','store_entrances')


def load_items() -> dict:
    '''
    Load item tracker data from save file.

    Returns:
        dict: save data
    '''

    try:
        ret = _load_save()['Items']
    except KeyError:
        ret = {}
    return ret


def load_dungeons() -> dict:
    '''
    Load dungeon tracker data from save file.

    Returns:
        dict: save data
    '''

    try:
        ret = _load_save()['Dungeons']
    except KeyError:
        ret = {}
    return ret


def load_locations() -> dict:
    '''
    Load location tracker data from save file.

    Returns:
        dict: save data
    '''

    try:
        ret = _load_save()['Locations']
    except KeyError:
        ret = {}
    return ret


def load_entrances() -> dict:
    '''
    Load entrance tracker data from save file.

    Returns:
        dict: save data
    '''

    try:
        ret = _load_save()['Entrances']
    except KeyError:
        ret = {}
    return ret


def _load_save() -> dict:
    '''
    Load save file.

    Return:
        dict: save data
    '''

    try:
        fid = open(os.path.join(CONFIGDIRECTORY, CONFIG['autosave']), 'r')
    except FileNotFoundError:
        return {}

    try:
        data = json.load(fid)
    except json.JSONDecodeError:
        return {}
    finally:
        fid.close()

    if data['version'] != version:
        return {}

    return data


def store_items(data: dict) -> None:
    '''
    Store item tracker state.

    Args:
        data: save data
    '''

    _store_save({'Items': data})


def store_dungeons(data: dict) -> None:
    '''
    Store dungeon tracker state.

    Args:
        data: save data
    '''

    _store_save({'Dungeons': data})


def store_locations(data: dict) -> None:
    '''
    Store location tracker state.

    Args:
        data: save data
    '''

    _store_save({'Locations': data})


def store_entrances(data: dict) -> None:
    '''
    Store location tracker state.

    Args:
        data: save data
    '''

    _store_save({'Entrances': data})


def _store_save(data: dict) -> None:
    '''
    Write save file.

    Args:
        data: save data
    '''

    savedata = _load_save()
    for dtype in data:
        savedata[dtype] = data[dtype]
    savedata['version'] = version
    with open(os.path.join(CONFIGDIRECTORY, CONFIG['autosave']), 'w') as fid:
        json.dump(savedata, fid)
