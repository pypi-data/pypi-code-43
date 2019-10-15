#!/usr/bin/env python3

import pyglet
import glooey.themes.wesnoth as wesnoth
import run_demos

window = pyglet.window.Window()
gui = wesnoth.Gui(window)
bg = wesnoth.Background(color='#101623')
text = wesnoth.Label(wesnoth.drawing.lorem_ipsum(num_paragraphs=4))
gui.add(bg)

@run_demos.on_space(gui)
def test_widget():
    scroll = wesnoth.VScrollBox()
    scroll.alignment = 'center'
    scroll.height_hint = gui.territory.height - 100
    text.enable_line_wrap(400)
    scroll.add(text)
    gui.add(scroll)

    yield scroll.__class__.__name__
    gui.remove(scroll)
    scroll.clear()

    scroll = wesnoth.HScrollBox()
    scroll.alignment = 'center'
    scroll.width_hint = gui.territory.width - 100
    text.enable_line_wrap(1500)
    scroll.add(text)
    gui.add(scroll)

    yield scroll.__class__.__name__
    gui.remove(scroll)
    scroll.clear()




pyglet.app.run()
