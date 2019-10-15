#!/usr/bin/env python3

import pyglet
import glooey.themes.wesnoth as wesnoth
import run_demos

window = pyglet.window.Window()
gui = wesnoth.Gui(window)
bg = wesnoth.Background(color='#101623')
#text = wesnoth.Label(wesnoth.drawing.lorem_ipsum(num_paragraphs=1))
#text.enable_line_wrap(400)
gui.add(bg)

@run_demos.on_space(gui)
def test_widget():
    frames = [
            wesnoth.HighlightFrame(),
            wesnoth.BrightHighlightFrame(),
    ]

    for frame in frames:
        #frame.add(text)
        gui.add(frame)

        yield frame.__class__.__name__

        gui.remove(frame)
        frame.clear()





pyglet.app.run()
