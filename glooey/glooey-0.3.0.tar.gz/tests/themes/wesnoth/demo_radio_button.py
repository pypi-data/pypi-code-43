#!/usr/bin/env python3

import pyglet
import glooey.themes.wesnoth as wesnoth

window = pyglet.window.Window()
gui = wesnoth.Gui(window)
radio = wesnoth.RadioButton()
gui.add(radio)

pyglet.app.run()


