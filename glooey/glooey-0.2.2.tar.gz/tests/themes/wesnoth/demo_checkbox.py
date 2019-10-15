#!/usr/bin/env python3

import pyglet
import glooey.themes.wesnoth as wesnoth

window = pyglet.window.Window()
gui = wesnoth.Gui(window)
checkbox = wesnoth.Checkbox()
gui.add(checkbox)

pyglet.app.run()


