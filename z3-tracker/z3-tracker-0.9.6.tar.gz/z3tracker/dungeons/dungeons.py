'''
Dungeon management
'''

import configparser
import importlib
import os.path
import json

from ..config.images import image
layoutstorage = importlib.import_module(
    '..gui-common.dungeons', package=__package__)

from .dungeonobj import DungeonObj
from .lists import DUNGEONS
from . import storage

__all__ = 'DungeonTracker',


def get_layout() -> dict:
    '''
    Load (or create) dungeon layout.

    Returns:
        dict: dungeon layout in format {identifier: (column, row)}
    '''

    try:
        layout = layoutstorage.load_dungeons()
    except (layoutstorage.NoConfig, configparser.Error):
        layout = {}
        for dungeon in DUNGEONS:
            layout[dungeon] = DUNGEONS[dungeon]
        layoutstorage.new_dungeon(layout)
        layout = layoutstorage.load_dungeons()
    return layout


class DungeonTracker(dict):
    '''
    Dungeon info tracker.
    '''

    def __init__(self, worldtracker):
        '''
        Args:
            worldtracker: world state tracker
        '''

        layout = get_layout()

        super().__init__()
        self.worldtracker = worldtracker
        self.crystal_requirement = {'tower': -1, 'ganon': -1}
        delayed_link = []
        for rawdungeon in DUNGEONS:
            dungeon = DungeonObj(
                rawdungeon, DUNGEONS[rawdungeon][0], DUNGEONS[rawdungeon][1],
                DUNGEONS[rawdungeon][2], DUNGEONS[rawdungeon][3], worldtracker)
            try:
                dungeon.location = layout[dungeon]
            except KeyError:
                pass
            self[dungeon.identifier] = dungeon
        data = storage.load_dungeons()
        self.restore(data)

    def set_crystal(self, ctype: str, diff: int) -> int:
        '''
        Set crystal requirements.

        Args:
            ctype: 'tower' or 'crystal'
            diff: -1, +1 or None (for reset)
        Returns:
            int: number of required crystals, -1 means unknown
        '''

        if diff is None:
            self.crystal_requirement[ctype] = -1
        else:
            self.crystal_requirement[ctype] += diff
        if self.crystal_requirement[ctype] < -1:
            self.crystal_requirement[ctype] = 7
        elif self.crystal_requirement[ctype] > 7:
            self.crystal_requirement[ctype] = -1
        self.worldtracker.set_crystal_requirement(
            self.crystal_requirement['tower'],
            self.crystal_requirement['ganon'])
        self.save()
        return self.crystal_requirement[ctype]

    def reset(self) -> None:
        '''
        Reset all dungeons.
        '''

        for dungeon in self:
            self[dungeon].reset()

    def save(self, *args) -> dict:
        '''
        Save current dungeon setup.
        '''

        storage.store_dungeons(self.store())

    def store(self) -> dict:
        '''
        Return current dungeon info for storage.

        Returns:
            dict: dungeon info
        '''

        dungeoninfo = {}
        for dungeon in self:
            dungeoninfo[dungeon] = self[dungeon].save()
        dungeoninfo['crystal_requirements'] = self.crystal_requirement
        return dungeoninfo

    def restore(self, dungeoninfo) -> None:
        '''
        Restore current dungeon info from file.

        Args:
            dungeoninfo: information from file
        '''

        for dungeon in dungeoninfo:
            if dungeon in self:
                self[dungeon].restore(dungeoninfo[dungeon])
        try:
            self.crystal_requirement.update(dungeoninfo['crystal_requirements'])
        except KeyError:
            pass
