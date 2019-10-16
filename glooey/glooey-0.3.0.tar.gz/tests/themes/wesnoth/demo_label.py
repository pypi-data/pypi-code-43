#!/usr/bin/env python3

import pyglet
import glooey.themes.wesnoth as wesnoth

window = pyglet.window.Window()
gui = wesnoth.Gui(window)
label = wesnoth.Label("Lorem ipsum.")
label.alignment = 'center'
gui.add(label)

pyglet.app.run()


