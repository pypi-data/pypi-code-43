'''
Item management
'''

import configparser
import importlib
import os.path
import json

from ..config.images import image
layoutstorage = importlib.import_module(
    '..gui-common.items', package=__package__)

from .itemobj import ItemObj
from .lists import ITEMS
from . import storage

__all__ = 'ItemTracker',


def get_layout() -> dict:
    '''
    Load (or create) item layout.

    Returns:
        dict: item layout in format {identifier: (column, row)}
    '''

    try:
        layout = layoutstorage.load_items()
    except (layoutstorage.NoConfig, configparser.Error):
        layout = {}
        for item in ITEMS:
            layout[item[0]] = item[1]
        layoutstorage.new_item(layout)
        layout = layoutstorage.load_items()
    return layout


class ItemTracker(dict):
    '''
    Inventory item tracker.
    '''

    def __init__(self, worldtracker):
        '''
        Args:
            worldtracker: world state tracker
        '''

        layout = get_layout()

        super().__init__()
        delayed_link = []
        for rawitem in ITEMS:
            item = ItemObj(
                rawitem[0], rawitem[1], rawitem[2], tuple(rawitem[3].keys()),
                tuple(rawitem[3].values()),
                rawitem[4]['links'] if 'links' in rawitem[4] else {},
                rawitem[4]['default'] if 'default' in rawitem[4] else 0,
                worldtracker)
            try:
                item.location = layout[item.identifier.lower()]
            except KeyError:
                pass
            self[item.identifier] = item
        for item in self:
            for linkitem in self[item].link:
                self[item].linkitems[linkitem] = self[linkitem]
        data = storage.load_items()
        self.restore(data)

    def reset(self) -> None:
        '''
        Reset all items.
        '''

        for item in self:
            self[item].reset()

    def save(self) -> dict:
        '''
        Save current item setup.
        '''

        storage.store_items(self.store())

    def store(self) -> dict:
        '''
        Return current item setup info for storage.

        Returns:
            inventory: item setup info
        '''

        inventory = {}
        for item in self:
            inventory[item] = self[item].inventory
        return inventory

    def restore(self, inventory) -> None:
        '''
        Restore current item setup from file.

        Args:
            inventory: information from file
        '''

        for item in inventory:
            if item in self:
                self[item].restore_inventory(inventory[item])
