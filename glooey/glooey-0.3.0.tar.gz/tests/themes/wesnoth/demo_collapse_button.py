#!/usr/bin/env python3

import pyglet
import glooey.themes.wesnoth as wesnoth

window = pyglet.window.Window()
gui = wesnoth.Gui(window)
button = wesnoth.CollapseButton()
gui.add(button)

pyglet.app.run()


