'''
Item tracking object.
'''

import operator
import os.path
import typing

from ..config.images import image

__all__ = 'ItemObj',


class ItemObj(object):
    '''
    Inventory item

    Progressive items are listed as one.

    Instance variables:
        identifier: item identifier string
        location: (column, row) location on display
        length: number of item progressions
        displayname: name(s) displayed in UI
        icon: path to image file(s) associated with item
        link: items (and requirement) linked with this item
        linkitems: item objects linked to this item
        default: default numer of items in inventory
        inventory: current number of items in inventory
        tracker: world state tracker
    '''

    def __init__(self, identifier: str, location: typing.Sequence[int],
                 length: int, displayname: typing.Sequence[str],
                 icon: typing.Sequence[str],
                 links: typing.Mapping[str, typing.Sequence[int]],
                 default: int, tracker):
        '''
        Args:
            identifier: internal item name
            location: (row, column) of item on tracker GUI
            length: number of progressions in item
            displayname: name(s) of item displayed on tracker GUI
            icon: icon(s) used on tracker GUI
            links: items linked with posession of item
            default: initial item progression
            tracker: world state tracker
        '''

        self.identifier = identifier
        self.location = location
        self.length = length
        self.displayname = displayname
        self.icon = tuple(image(i) for i in icon)
        self.link = links
        self.linkitems = {}
        self.default = default
        self.inventory = default
        self.tracker = tracker
        self.restore_inventory(self.default)

    def index(self) -> int:
        '''
        Return current displayname/image index.

        Returns:
            int: index used for sequence attributes
        '''

        idx = self.inventory if self.inventory < 1 else self.inventory - 1
        return idx

    def display(self) -> str:
        '''
        Return currently applicable item display string.

        Returns:
            str: name to be displayed in application
        '''

        idx = self.index()
        item_name = self.displayname[idx]
        return item_name

    def state(self) -> bool:
        '''
        Return current state of item.

        Returns:
            str: True if item is active, else False
        '''

        return self.inventory > 0

    def increase(self, *args) -> None:
        '''
        Left-click on item
        '''

        if self.inventory < self.length:
            self.inventory += 1
        self.update_links()
        self.tracker.set_item(self.identifier, self.inventory)

    def decrease(self, *args) -> None:
        '''
        Right-click on item
        '''
        
        if self.inventory > 0:
            self.inventory -= 1
        self.update_links()
        self.tracker.set_item(self.identifier, self.inventory)

    def reset(self) -> None:
        '''
        Reset item.
        '''

        to_remove = self.inventory - self.default
        if to_remove > 0:
            for _ in range(to_remove):
                self.decrease(_)
        elif to_remove < 0:
            for _ in range(-to_remove):
                self.increase(_)

    def restore_inventory(self, quantity: int) -> None:
        '''
        Set inventory number.

        Args:
            quantity: number to set inventory to
        '''

        self.inventory = quantity
        self.update_links()
        self.tracker.set_item(self.identifier, quantity)

    def add_links(linkitems: typing.Sequence) -> None:
        '''
        Register linked items.

        Args:
            linkitems: list of item objects
        '''

        for li in linkitems:
            self.linkitems[li.identifier] = li

    def update_links(self) -> None:
        '''
        Update state of linked items according to current inventory.
        '''

        for li in self.linkitems:
            if self.inventory in self.link[li]:
                self.linkitems[li].restore_inventory(1)
            else:
                self.linkitems[li].restore_inventory(0)
