'''
Dungeon display.
'''

import importlib
import tkinter as tk
import tkinter.ttk as ttk
import typing

from ..config import CONFIG
from ..config.images import image, makebw
from .. import dungeons
common = importlib.import_module(
    '..gui-common.dungeons', package=__package__)
REWARDS = common.REWARDS

from . import misc

__all__ = 'DungeonWindow',


class DungeonWindow(tk.Toplevel):
    '''
    Dungeon check display.

    Instance variables:
        tracker: dungeon tracker object
        layout: dungeon layout in display
        helpertext: helper text variable
        scaling: up- and downscale factors for objects
        widgets: single dungeon button collections
    '''

    def __init__(self, tracker):
        '''
        Args:
            tracker: dungeon tracker object
        '''

        super().__init__()
        self.title('Dungeons')

        self.tracker = tracker

        self.frame = ttk.Frame(self)
        self.frame.pack(side='top', fill='both', expand=True)

        self.bottomframe = ttk.Frame(self)
        self.bottomframe.pack(side='top', fill='x', expand=True)
        self.helperframe = ttk.Frame(self.bottomframe)
        self.helperframe.pack(side='left', fill='x', expand=True)
        self.helpertext = tk.StringVar()
        self.helper = ttk.Label(
            self.helperframe, anchor=tk.CENTER, textvariable=self.helpertext)
        self.helper.pack(side='left', fill='x', expand=True)

        self.scaling = _scale_factors()
        scale = self.scaling[0] / self.scaling[1]
        _icon_scale = lambda icon: icon.zoom(
            self.scaling[0], self.scaling[0]).subsample(
                self.scaling[1], self.scaling[1])

        self.ganoncrystals = {
            'icon': _icon_scale(
                tk.PhotoImage(
                    file=image('ganonstower'),
                    master=self.bottomframe)).subsample(2, 2),
            'canvas': tk.Canvas(
                self.bottomframe, height=32 * scale, width=48 * scale),
            'count': -1}
        self.ganoncrystals['image'] = self.ganoncrystals['canvas'].create_image(
            0, 0, anchor=tk.NW, image=self.ganoncrystals['icon'])
        self.ganoncrystals['text'] = self.ganoncrystals['canvas'].create_text(
            48 * scale, 32 * scale, anchor=tk.SE, text='?')
        self.ganoncrystals['canvas'].bind(
            '<Enter>', lambda _: self.helpertext.set("Ganon's Pyramid Access"))
        self.ganoncrystals['canvas'].bind(
            '<Leave>', lambda _: self.helpertext.set(''))
        self.ganoncrystals['canvas'].bind(
            '<ButtonRelease-1>', lambda _: self.set_crystal('ganon', +1))
        self.ganoncrystals['canvas'].bind(
            '<ButtonRelease-3>', lambda _: self.set_crystal('ganon', -1))
        self.ganoncrystals['canvas'].pack(side='right')
        self.set_crystal('ganon', 0)

        self.towercrystals = {
            'icon': _icon_scale(
                tk.PhotoImage(
                    file=image('reward-crystal'), master=self.bottomframe)),
            'canvas': tk.Canvas(
                self.bottomframe, height=32 * scale, width=48 * scale),
            'count': -1}
        self.towercrystals['image'] = self.towercrystals['canvas'].create_image(
            0, 0, anchor=tk.NW, image=self.towercrystals['icon'])
        self.towercrystals['text'] = self.towercrystals['canvas'].create_text(
            48 * scale, 32 * scale, anchor=tk.SE, text='?')
        self.towercrystals['canvas'].bind(
            '<Enter>', lambda _: self.helpertext.set("Ganon's Tower Access"))
        self.towercrystals['canvas'].bind(
            '<Leave>', lambda _: self.helpertext.set(''))
        self.towercrystals['canvas'].bind(
            '<ButtonRelease-1>', lambda _: self.set_crystal('tower', +1))
        self.towercrystals['canvas'].bind(
            '<ButtonRelease-3>', lambda _: self.set_crystal('tower', -1))
        self.towercrystals['canvas'].pack(side='right')
        self.set_crystal('tower', 0)

        buttonstyle = ttk.Style()
        buttonstyle.configure('Dungeonbutton.TButton', relief=tk.FLAT)

        self.widgets = []
        self.redraw()

    def _dungeon_display(self, dungeon) -> None:
        '''
        Make and place single dungeons display object.

        Args:
            dungeon: dungeon object
        Writes:
            buttons
        '''

        widget = Dungeon(dungeon, self.frame, self.scaling)
        widget.bind(
            '<Enter>', lambda _: self.helpertext.set(dungeon.identifier))
        widget.bind(
            '<Leave>', lambda _: self.helpertext.set(''))

        for button in widget.buttons:
            button.bind('<ButtonRelease-1>', self.tracker.save, add='+')
            button.bind('<ButtonRelease-3>', self.tracker.save, add='+')
            button.bind(
                '<ButtonRelease-1>', lambda _: widget.check_state(dungeon),
                add='+')
            button.bind(
                '<ButtonRelease-3>', lambda _: widget.check_state(dungeon),
                add='+')

        widget.grid(
            column=dungeon.location[0], row=dungeon.location[1], sticky=misc.A)
        self.widgets.append(widget)

    def reset(self) -> None:
        '''
        Reset dungeons to default.
        '''

        for cobj in ('tower', 'ganon'):
            self.set_crystal(cobj, None)
        self.tracker.reset()
        self.redraw()

    def redraw(self) -> None:
        '''
        Recreate dungeon display.
        '''

        while self.widgets:
            self.widgets.pop().destroy()
        for dungeon in self.tracker:
            self._dungeon_display(self.tracker[dungeon])

    def set_crystal(self, ctype: str, diff: int) -> None:
        '''
        Set crystal requirements.

        Args:
            ctype: 'tower' or 'crystal'
            diff: -1, 0, +1 or None (for reset)
        '''

        assert ctype in ('tower', 'ganon')
        assert diff in (-1, 0, +1, None)
        scale = self.scaling[0] / self.scaling[1]
        cobj = self.towercrystals if ctype == 'tower' else self.ganoncrystals
        cobj['count'] = self.tracker.set_crystal(ctype, diff)
        if cobj['count'] == -1:
            newtext = '?'
        else:
            newtext = str(cobj['count'])
        cobj['canvas'].delete(cobj['text'])
        cobj['text'] = cobj['canvas'].create_text(
            48 * scale, 32 * scale, anchor=tk.SE, font=('Arial Black', 16),
            text=newtext)


class Dungeon(ttk.Frame):
    '''
    Single dungeon display object.
    '''

    def __init__(
            self, dungeon, parent: ttk.Frame, scaling: (int, int)):
        '''
        dungeon: dungeon object
        parent: parent widget for object
        scaling: button scale
        '''

        self.scaling = scaling
        scale = scaling[0] / scaling[1]

        super().__init__(parent, borderwidth=2, relief=tk.RIDGE)
        self.child = ttk.Label(self)
        self.child.grid(column=0, row=0, sticky=misc.A)

        icon = self._icon_scale(
            tk.PhotoImage(file=dungeon.icon, master=parent)
            if dungeon.icon else None)
        self.pic = ttk.Label(
            self.child, borderwidth=1, image=icon, relief=tk.RAISED)
        self.pic.grid(column=0, row=0, columnspan=2, rowspan=2)
        self.icon = icon

        self.rewardname = dungeon.get('reward')
        self.rewardimg = REWARDS[self.rewardname]
        self.rewardicon = self._icon_scale(
            tk.PhotoImage(file=image(self.rewardimg), master=self))
        self.reward = tk.Canvas(
            self.child, height=32 * scale, width=32 * scale)
        if 'reward' in dungeon.features:
            self.rewardid = self.reward.create_image(
                0, 0, anchor=tk.NW, image=self.rewardicon)
            self.reward.bind(
                '<ButtonRelease-1>', lambda _: dungeon.cycle_reward(True))
            self.reward.bind(
                '<ButtonRelease-3>', lambda _: dungeon.cycle_reward(False))
        self.reward.grid(column=2, row=0)

        self.complete = tk.Canvas(
            self.child, height=32 * scale, width=32 * scale)
        self.complete.create_rectangle(5, 5, 27, 27, width=4)
        self.completeid = None
        self.complete.bind(
            '<ButtonRelease-1>', lambda _: dungeon.mark_complete(True))
        self.complete.bind(
            '<ButtonRelease-3>', lambda _: dungeon.mark_complete(False))
        self.complete.grid(column=2, row=1)

        self.medallionname = dungeon.medallion
        self.medallionicon = self._icon_scale(
            tk.PhotoImage(
                file=image('medallion-{0:s}'.format(self.medallionname)),
                master=self))
        self.medallion = tk.Canvas(
            self.child, height=32 * scale, width=32 * scale)
        if 'medallion' in dungeon.features:
            self.medallionid = self.medallion.create_image(
                0, 0, anchor=tk.NW, image=self.medallionicon)
            self.medallion.bind(
                '<ButtonRelease-1>', lambda _: dungeon.cycle_medallion(True))
            self.medallion.bind(
                '<ButtonRelease-3>', lambda _: dungeon.cycle_medallion(False))
        self.medallion.grid(column=3, row=0)

        self.bigkeyicon = self._icon_scale(
            tk.PhotoImage(file=image('bigkey'), master=parent))
        self.bigkey = tk.Canvas(
            self.child, height=32 * scale, width=32 * scale)
        if ('bigkey' in dungeon.features and
            CONFIG['dungeon_items'] == 'Keysanity'):
            self.bigkeyid = self.bigkey.create_image(
                0, 0, anchor=tk.NW, image=self.bigkeyicon)
            self.bigkey.bind('<ButtonRelease-1>', dungeon.toggle_bigkey)
            self.bigkey.bind('<ButtonRelease-3>', dungeon.toggle_bigkey)
        self.bigkey.grid(column=3, row=1, sticky=tk.E)

        self.keyicon = self._icon_scale(
            tk.PhotoImage(file=image('smallkey'), master=parent))
        self.key = tk.Canvas(
            self.child, height=32 * scale, width=48 * scale)
        if (dungeon.totalkeys > 0 and
            CONFIG['dungeon_items'] in (
                'Maps/Compasses/Small Keys', 'Keysanity') and
            CONFIG['world_state'] != 'Retro'):
            self.keyimg = self.key.create_image(
                0, 0, anchor=tk.NW, image=self.keyicon)
            self.keytext = self.key.create_text(
                48 * scale, 32 * scale, anchor=tk.SE, text='0')
            self.key.bind('<ButtonRelease-1>', dungeon.key_up)
            self.key.bind('<ButtonRelease-3>', dungeon.key_down)
        self.key.grid(column=4, columnspan=2, row=0)

        self.itemicon = self._icon_scale(
            tk.PhotoImage(file=image('chest_full'), master=parent))
        self.item = tk.Canvas(
            self.child, height=32 * scale, width=48 * scale)
        if dungeon.total_items() > 0:
            self.itemimg = self.item.create_image(
                0, 0, anchor=tk.NW, image=self.itemicon)
            self.itemtext = self.item.create_text(
                48 * scale, 32 * scale, anchor=tk.SE, text='0')
            self.item.bind('<ButtonRelease-1>', dungeon.item_up)
            self.item.bind('<ButtonRelease-3>', dungeon.item_down)
        if CONFIG['dungeon_items'] in (
                'Maps/Compasses/Small Keys', 'Keysanity'):
            self.item.grid(column=4, columnspan=2, row=1)
        else:
            self.item.grid(column=3, columnspan=2, row=1)

        self.buttons = (
            self.reward, self.complete, self.medallion, self.bigkey, self.key,
            self.item)

        self.check_state(dungeon)

    def check_state(self, dungeon) -> None:
        '''
        Check button state and make adjustments if necessary.

        Args:
            dungeon: dungeon object
        '''

        # Check whether reward image needs to be changed.
        if self.rewardname != dungeon.reward:
            self.rewardname = dungeon.reward
            self.rewardimg = REWARDS[dungeon.reward]
            self.rewardicon = self._icon_scale(
                tk.PhotoImage(file=image(self.rewardimg), master=self))
            self.reward.delete(self.rewardid)
            self.rewardid = self.reward.create_image(
                0, 0, anchor=tk.NW, image=self.rewardicon)

        # Check completion.
        icon = self._icon_scale(tk.PhotoImage(file=dungeon.icon, master=self))
        if dungeon.completed:
            icon = makebw(icon)
        if dungeon.completed and self.completeid is None:
            self.completeid = self.complete.create_text(
                17, 17, anchor=tk.CENTER, font=('Arial Black', 20), text='✔')
        elif not dungeon.completed and self.completeid is not None:
            self.complete.delete(self.completeid)
            self.completeid = None
        self.pic = ttk.Label(
            self.child, borderwidth=1, image=icon, relief=tk.RAISED)
        self.pic.grid(column=0, row=0, columnspan=2, rowspan=2)
        self.icon = icon

        # Check whether medallion image needs to be changed.
        if self.medallionname != dungeon.medallion:
            self.medallionname = dungeon.medallion
            self.medallionicon = self._icon_scale(
                tk.PhotoImage(
                    file=image('medallion-{0:s}'.format(self.medallionname)),
                    master=self))
            self.medallion.delete(self.medallionid)
            self.medallionid - self.medallion.create_image(
                0, 0, anchor=tk.NW, image=self.medallionicon)
            

        # Check whether the bigkey button should be disabled.
        try:
            self.bigkey.delete(self.bigkeyid)
        except AttributeError:
            pass
        else:
            self.bigkeyicon = self._icon_scale(
                tk.PhotoImage(file=image('bigkey'), master=self))
            if not dungeon.bigkey:
                self.bigkeyicon = makebw(self.bigkeyicon)
            self.bigkey.create_image(
                0, 0, anchor=tk.NW, image=self.bigkeyicon)

        # Check numbers (small keys).
        scale = self.scaling[0] / self.scaling[1]
        try:
            self.key.delete(self.keytext)
        except AttributeError:
            pass
        else:
            self.keytext = self.key.create_text(
                48 * scale, 32 * scale, anchor=tk.SE,
                font=('Arial Black', int(16 * scale)),
                text=str(dungeon.smallkeys))

        # Check numbers (items).
        try:
            self.item.delete(self.itemtext)
        except AttributeError:
            pass
        else:
            itemfont = (
                ('Arial Black', int(8 * scale)) if dungeon.remaining() > 9
                else ('Arial Black', int(16 * scale)))
            self.itemtext = self.item.create_text(
                48 * scale, 32 * scale, anchor=tk.SE, font=itemfont,
                text=str(dungeon.remaining()))
            newchest = (
                'chest_full' if dungeon.remaining() > 0 else 'chest_empty')
            self.itemicon = self._icon_scale(
                tk.PhotoImage(file=image(newchest), master=self))
            self.item.delete(self.itemimg)
            self.itemimg = self.item.create_image(
                0, 0, anchor=tk.NW, image=self.itemicon)

    def _icon_scale(self, icon: tk.PhotoImage) -> tk.PhotoImage:
        '''
        Rescale icon.

        Args:
            icon: icon to be rescaled
        Returns:
            tk.PhotoImage: rescaled icon
        '''

        if self.scaling[0] != 1:
            icon = icon.zoom(self.scaling[0], self.scaling[0])
        if self.scaling[1] != 1:
            icon = icon.subsample(self.scaling[1], self.scaling[1])
        return icon


def _scale_factors() -> (int, int):
    '''
    Calculate up- and downscale factor.

    Returns:
        int: upscale factor
        int: downscale factor
    '''

    scaling = CONFIG['icon_size']
    for up in range(1, 1000):
        if not (scaling * up) % 1:
            upscale = int(scaling * up)
            break
    else:
        CONFIG.set('icon_size', 1)
        assert False
    downscale = int(upscale // scaling)
    return upscale, downscale


def start(worldtracker) -> DungeonWindow:
    '''
    Initialise dungeon tracker window.

    Args:
        worldtracker: world state tracker
    '''

    return DungeonWindow(dungeons.DungeonTracker(worldtracker))
