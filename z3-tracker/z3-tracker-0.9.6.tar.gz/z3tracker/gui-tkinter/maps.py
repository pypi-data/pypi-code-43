'''
Map tracker display
'''

import importlib
import tkinter as tk
import tkinter.ttk as ttk
import typing

from ..config import CONFIG
from ..config.images import image
common = importlib.import_module(
    '..gui-common.maps', package=__package__)
BUTTONTYPE = common.BUTTONTYPE

from . import misc

MAPSCALE = 1

__all__ = 'MapDisplay', 'make_symbol_coordinates'


class MapDisplay(tk.Toplevel):
    '''
    Map window

    Instance variables:
        identifier: map name
        scale: map scale
        imagefile: map image
        entrancetracker: entrance tracker
        other: other (dark/light world) map
        activelink: linked button currently artifically set to active
        button: ocation buttons
        tracker: location trackern
    '''

    def __init__(self, spec: str):
        '''
        Args:
            spec: map type
        '''

        # General initialisation
        assert spec in ('light', 'dark')
        super().__init__()
        self.identifier = spec
        self.scale = CONFIG['map_size']
        self.title('Light World' if spec == 'light' else 'Dark World')
        self.button = {}
        self.entrancetracker = None
        self.other = None
        self.activelink = set()
        self.tracker = None

        # Set up bottom text label.
        self.helpertext = tk.StringVar()
        self.helper = ttk.Label(self, textvariable=self.helpertext)
        self.helper.grid(column=0, row=1, sticky=tk.S)

        # Set background image.
        imagefile = tk.PhotoImage(
            file=image('lightworld' if spec == 'light' else 'darkworld'),
            master=self)
        scaling = MAPSCALE * self.scale
        imgdim = (imagefile.width() * scaling, imagefile.height() * scaling)
        self.map = tk.Canvas(self, height=imgdim[1], width=imgdim[0])
        self.map.grid(column=0, row=0, sticky=misc.A)
        for up in range(1, 1000):
            if not (scaling * up) % 1:
                upscale = int(scaling * up)
                break
        else:
            CONFIG['map_size'] = 1
            self.scale = 1
            assert False
        downscale = int(upscale // scaling)
        if upscale != 1:
            imagefile = imagefile.zoom(upscale, upscale)
        if downscale != 1:
            imagefile = imagefile.subsample(downscale, downscale)
        self.image = self.map.create_image(
            (0, 0), anchor=tk.NW, image=imagefile)
        self.map.bind('<ButtonRelease-3>', lambda _: self._rightclick_button())
        self.imagefile = imagefile

    def add_location_tracker(self, locationtracker) -> None:
        '''
        Add location tracker.

        Args:
            locationtracker: location tracker
        '''

        self.tracker = locationtracker

    def place_buttons(self, locations: dict) -> None:
        '''
        Place buttons on map.

        Args:
            locations: {
               'location name': {'map': str, 'coord': (int, int), 'type': str}}
        '''

        for loc in locations:
            self.add_button(
                loc, locations[loc]['coord'], locations[loc]['type'])

    def add_button(
            self, name: str, coord: typing.Sequence[int],
            buttontype: str) -> None:
        '''
        Add a button.

        Args:
            name: name of new button
            coord: coordinates for centre of button
            buttontype: type of button
        '''

        # Dungeon buttons are different.
        if buttontype == 'dungeon':
            self._add_dungeon_button(name, coord)
            return

        # Make button.
        assert (buttontype in ('chest', 'item', 'cave', 'drop', 'ganon') or
                buttontype.startswith('entrance'))
        displaytext = name
        if buttontype == 'chest':
            buttonfunc = self._chest_icon
        elif buttontype == 'entrance_drop':
            buttonfunc = self._drop_entrance_icon
            displaytext = displaytext.replace(' Entrance (E)', '')
        elif buttontype.startswith('entrance'):
            buttonfunc = self._entrance_icon
            displaytext = displaytext.replace(' Entrance (E)', '')
        elif buttontype == 'item':
            buttonfunc = self._item_icon
        elif buttontype == 'cave':
            buttonfunc = self._cave_icon
        elif buttontype == 'drop':
            buttonfunc = self._drop_icon
        elif buttontype == 'ganon':
            buttonfunc = self._ganon_icon
        else:
            buttonfunc = self._item_icon
        new = buttonfunc(coord)
        self.button[name] = {
            'id': new, 'type': buttontype, 'display': displaytext,
            'available': 'unavailable', 'entrance': False}
        if name not in self.tracker:
            self.tracker[name] = True

        # Assign button functions.
        self.map.tag_bind(
            new, '<Enter>', lambda _: self._hover(name))
        self.map.tag_bind(
            new, '<Leave>', lambda _: self._unhover(name))
        self.map.tag_bind(
            new, '<ButtonRelease-1>', lambda _: self._leftclick_button(name))
        if buttontype.startswith('entrance'):
            self.map.tag_bind(
                new, '<ButtonRelease-2>', lambda _: self._middleclick_button(name))
            self.map.tag_bind(
                new, '<ButtonRelease-3>', lambda _: self._rightclick_button(name))

    def _hover(self, button: str) -> None:
        '''
        Set bottom display.

        Args:
            button: button under mouse
        '''

        displaytext = self.button[button]['display']
        if self.button[button]['type'].startswith('entrance'):

            # Entrance leading to itself.
            try:
                same = self.entrancetracker[button] == button.replace(
                    ' (E)', ' (I)')
            except KeyError:
                same = False
            if button in self.entrancetracker and same:
                self.set_entrance_colour(button, 'default')

            # Entrances reachable from entrance.
            linked = self.entrancetracker.find_remote(button)
            for loc in linked:
                if loc in self.button:
                    self.set_entrance_colour(loc, 'linked')
                else:
                    self.other.set_entrance_colour(loc, 'linked')

            # Entrance leading to interior.
            if button in self.entrancetracker and not same:
                linked = self.entrancetracker[button].replace(
                    ' Entrance (I)', '')
                displaytext = '{0:s} → {1:s}'.format(displaytext, linked)
                if displaytext != linked:
                    linkbutton = '{0:s} Entrance (E)'.format(linked)
                    if linkbutton in self.button:
                        self.set_entrance_colour(linkbutton, 'interior')
                    else:
                        self.other.set_entrance_colour(linkbutton, 'interior')

            # Interior reached via entrance.
            interior = button.replace(' (E)', ' (I)')
            if interior in self.entrancetracker and not same:
                linked = self.entrancetracker[interior]
                if displaytext != linked.replace(' Entrance (E)', ''):
                    if linked in self.button:
                        self.set_entrance_colour(linked, 'entrance')
                    else:
                        self.other.set_entrance_colour(linked, 'entrance')

        self.helpertext.set(displaytext)

    def _unhover(self, button: str) -> None:
        '''
        Set bottom display.

        Args:
            button: button under mouse
        '''

        self.helpertext.set('')
        while self.activelink:
            self._set_colour(self.activelink.pop())
        while self.other.activelink:
            self.other._set_colour(self.other.activelink.pop())

    def _leftclick_button(self, name: str) -> None:
        '''
        Event on left-clicking a button.

        Args:
            name: name of clicked-on button
        '''

        self.tracker[name] = not self.tracker[name]
        self._set_colour(name)
        self.tracker.save()

    def _middleclick_button(self, name: str) -> None:
        '''
        Event on middle-clicking a button.

        Args:
            name: name of clicked on button
        '''

        new = self.entrancetracker.event(name)
        if not new and self.entrancetracker.armed:
            self.helper.configure(background='yellow')
        else:
            self.helper.configure(background='')
        if new:
            self.set_entrance()

    def _rightclick_button(self, name: str = None) -> None:
        '''
        Event on right-clicking a button.

        Args:
            name: name of clicked on button
        '''

        self.entrancetracker.abort(name)
        self.helper.configure(background='')
        if name:
            self.set_entrance()
            self._hover(name)

    def _add_dungeon_button(
            self, name: str, coord: typing.Sequence[int]) -> None:
        '''
        Add dungeon button.

        Args:
            name: name of dungeon
            coord: location on map
        '''

        shape = -13, -13, 13, 13
        loc = make_symbol_coordinates(coord, shape, self.scale)
        new_outer = self.map.create_rectangle(*loc)
        shape = -7, -7, 7, 7
        loc = make_symbol_coordinates(coord, shape, self.scale)
        new_inner = self.map.create_rectangle(*loc)
        self.button[name] = {
            'id': (new_outer, new_inner), 'type': 'dungeon', 'display': name,
            'available': ['unavailable', 'unavailable']}
        if name not in self.tracker:
            self.tracker[name] = [True, True]
        
        for new in (new_outer, new_inner):
            self.map.tag_bind(
                new, '<Enter>', lambda _: self.helpertext.set(name))
            self.map.tag_bind(
                new, '<Leave>', lambda _: self.helpertext.set(''))

    def remove_buttons(self) -> None:
        '''
        Remove all buttons from map.
        '''

        for button in self.button.values():
            if button['type'] == 'dungeon':
                self.map.delete(button['id'][0])
                self.map.delete(button['id'][1])
            else:
                self.map.delete(button['id'])
        self.button = {}

    def set_availability(self, name: str, availability: str) -> None:
        '''
        Set whether given location is available.

        Args:
            name: location name
            availability: 'available', 'unavailable', 'visible', 'maybe',
                'indirect'
        '''

        assert availability in (
            'available', 'unavailable', 'visible', 'maybe', 'indirect')
        self.button[name]['available'] = availability
        self._set_colour(name)

    def set_dungeon_availability(
            self, name: str, availability: (str, str)) -> None:
        '''
        Set whether given dungeon is available.

        Args:
            name: location name
            availability: two of 'available', 'unavailable', 'visible', 'maybe',
                'indirect'
        '''

        for idx, avail in enumerate(availability):
            assert avail in (
                'available', 'unavailable', 'visible', 'maybe', 'indirect')
            self.button[name]['available'][idx] = avail
        self._set_colour(name)
        self.tracker.save()

    def set_entrance(self) -> None:
        '''
        Update entrance display.
        '''

        for button in self.button:
            if self.button[button]['type'] == 'dungeon':
                continue
            if (button in self.entrancetracker and
                not self.button[button]['entrance']):
                self.button[button]['entrance'] = True
                self.entrancetracker.update()
            elif (button not in self.entrancetracker and
                  self.button[button]['entrance']):
                self.button[button]['entrance'] = False
                self.entrancetracker.update()
        for button in self.other.button:
            if self.other.button[button]['type'] == 'dungeon':
                continue
            if (button in self.entrancetracker and
                not self.other.button[button]['entrance']):
                self.other.button[button]['entrance'] = True
                self.entrancetracker.update()
            elif (button not in self.entrancetracker and
                  self.other.button[button]['entrance']):
                self.other.button[button]['entrance'] = False
                self.entrancetracker.update()

    def _set_colour(self, button: str) -> None:
        '''
        Set button colour.

        Args:
            button: button name
        '''

        if self.button[button]['type'] == 'dungeon':
            self._set_dungeon_colour(button)
            return
        if not self.tracker[button]:
            colour = 'checked'
        else:
            colour = self.button[button]['available']
        if self.button[button]['type'] in BUTTONTYPE:
            colours = BUTTONTYPE[self.button[button]['type']]['colours']
        else:
            colours = BUTTONTYPE['standard']['colours']
        if self.button[button]['entrance']:
            activeoutline = 'black'
            activewidth = 3
            outline = 3
        else:
            activeoutline = 'black'
            activewidth = 1
            outline = 1
        self.map.itemconfigure(
            self.button[button]['id'],
            activefill=colours[colour]['active'],
            activeoutline=activeoutline,
            activewidth=activewidth,
            fill=colours[colour]['normal'],
            outline='black', width=outline)

    def set_entrance_colour(self, button: str, linktype: str) -> None:
        '''
        Set colour of linked entrance button.

        Args:
            button: button name
            linktime: 'entrance', 'interior', 'linked'
        '''

        assert linktype in ('entrance', 'interior', 'linked', 'default')
        if not self.tracker[button]:
            colour = 'checked'
        else:
            colour = self.button[button]['available']
        if self.button[button]['type'] in BUTTONTYPE:
            colours = BUTTONTYPE[self.button[button]['type']]['colours']
        else:
            colours = BUTTONTYPE['standard']['colours']
        if button in self.activelink:
            if linktype == 'interior':
                linkcolour = 'magenta'
            elif linktype == 'entrance':
                linkcolour = 'cyan'
            else:
                linkcolour = 'orange'
            self.map.itemconfigure(
                self.button[button]['id'], fill=colours[colour]['active'],
                outline=linkcolour, width=3)
        elif linktype == 'entrance':
            self.map.itemconfigure(
                self.button[button]['id'], fill=colours[colour]['active'],
                outline='yellow', width=3)
        elif linktype == 'interior':
            self.map.itemconfigure(
                self.button[button]['id'], fill=colours[colour]['active'],
                outline='red', width=3)
        elif linktype == 'linked':
            self.map.itemconfigure(
                self.button[button]['id'], fill=colours[colour]['active'],
                outline='blue', width=3)
        elif linktype == 'default':
            self.map.itemconfigure(
                self.button[button]['id'], activefill=colours[colour]['active'],
                activeoutline='white', activewidth=3)
        self.activelink.add(button)

    def _set_dungeon_colour(self, button: str) -> None:
        '''
        Set colour of dungeon button.

        Args:
            button: dungeon name
        '''

        for bpart in range(2):
            if not self.tracker[button][bpart]:
                colour = 'checked'
            else:
                colour = self.button[button]['available'][bpart]
            colours = BUTTONTYPE['standard']['colours']
            self.map.itemconfigure(
                self.button[button]['id'][bpart],
                activefill=colours[colour]['normal'],
                fill=colours[colour]['normal'],
                outline='black', width=1)

    def reset(self) -> None:
        '''
        Reset state of all buttons.
        '''

        self.entrancetracker.reset()
        self.tracker.reset()
        self.set_entrance()
        for button in self.button:
            if self.button[button]['type'] == 'dungeon':
                self.tracker[button] = [True, True]
            else:
                self.tracker[button] = True
            self._set_colour(button)

    def add_entrance_tracker(self, entrancetracker) -> None:
        '''
        Add entrance tracker.
        '''

        self.entrancetracker = entrancetracker

    def _chest_icon(self, location: typing.Sequence[int]) -> int:
        shape = -7, -7, 7, 7
        loc = make_symbol_coordinates(location, shape, self.scale)
        new = self.map.create_rectangle(*loc)
        return new

    def _entrance_icon(self, location: typing.Sequence[int]) -> int:
        shape = -5, -5, 5, 5
        loc = make_symbol_coordinates(location, shape, self.scale)
        new = self.map.create_rectangle(*loc)
        return new

    def _item_icon(self, location: typing.Sequence[int]) -> int:
        shape = -7, -7, 7, 7
        loc = make_symbol_coordinates(location, shape, self.scale)
        new = self.map.create_oval(*loc)
        return new

    def _cave_icon(self, location: typing.Sequence[int]) -> int:
        shape = -7, 7, 0, -7, 7, 7
        loc = make_symbol_coordinates(location, shape, self.scale)
        new = self.map.create_polygon(*loc)
        return new

    def _drop_icon(self, location: typing.Sequence[int]) -> int:
        shape = -7, -7, 0, 7, 7, -7
        loc = make_symbol_coordinates(location, shape, self.scale)
        new = self.map.create_polygon(*loc)
        return new

    def _drop_entrance_icon(self, location: typing.Sequence[int]) -> int:
        shape = -6, -6, 0, 6, 6, -6
        loc = make_symbol_coordinates(location, shape, self.scale)
        new = self.map.create_polygon(*loc)
        return new

    def _ganon_icon(self, location: typing.Sequence[int]) -> int:
        '''Go-mode symbol'''
        shape = (0, -20, 5, -5, 20, -5, 8, 5, 12, 20, 0, 11,
                 -12, 20, -8, 5, -20, -5, -5, -5)
        loc = make_symbol_coordinates(location, shape, self.scale)
        new = self.map.create_polygon(*loc)
        return new


def make_symbol_coordinates(
        location: typing.Sequence[int], shape: typing.Sequence[int],
        mapscale: float) -> list:
    '''
    Create corner points for map symbol.

    Args:
        location: centre of symbol
        shape: symbol corners relative to centre point
        mapscale: additional map scaling factor
    Returns:
        list: flat list of coordinates for symbol creation
    '''

    loc = list(location[:2]) * (len(shape) // 2)
    scaled = tuple(int(c * MAPSCALE * mapscale) for c in shape)
    loc = [loc[l] * mapscale + scaled[l] for l in range(len(scaled))]
    return loc

