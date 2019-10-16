#!/usr/bin/env python3

import pyglet
import glooey.themes.wesnoth as wesnoth
import run_demos

window = pyglet.window.Window()
gui = wesnoth.Gui(window)

@run_demos.on_space(gui)
def test_widget():
    buttons = [
            wesnoth.Button('Lorem ipsum'),
            wesnoth.SmallButton('Lorem'),
            wesnoth.BackgroundButton('Lorem ipsum'),
            wesnoth.SquareButton(),
            wesnoth.BigSquareButton(),
            wesnoth.BiggerSquareButton(),
            wesnoth.MenuButton('Lorem ipsum'),
            wesnoth.SmallMenuButton('Lorem'),
            wesnoth.BlankMenuButton('Lorem ipsum'),
    ]
    for button in buttons:
        gui.clear(); gui.add(button)
        yield button.__class__.__name__

pyglet.app.run()


