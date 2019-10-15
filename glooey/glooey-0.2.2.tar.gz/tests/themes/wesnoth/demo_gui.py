#!/usr/bin/env python3

import pyglet
import glooey.themes.wesnoth as wesnoth
import run_demos

window = pyglet.window.Window()
gui = wesnoth.Gui(window)
box = wesnoth.EventLogger(50, 50, align='center')


gui.add(box)

@run_demos.on_space(gui)
def test_widget():
    styles = 'bw', 'color'
    styles = 'color',
    cursors = [
            'normal',
            'wait',
            'select',
            'select_illegal',
            'select_location',
            'move',
            'move_drag',
            'attack',
            'attack_drag',
            'no_cursor',
    ]
    for style in styles:
        gui.cursor_style = style
        for cursor in cursors:
            gui.cursor = cursor
            yield f"Cursor: {cursor}; Style: {style}"

pyglet.app.run()


