"""Tests for the `ptvpy.plot` module."""


import os

import pytest
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import KeyEvent

import ptvpy.plot as ptvpy_plot
from ptvpy.generate import describe_lines, add_properties, render_frames


# Check if the tests are run in continuous integration (used to skip certain tests)
running_ci = bool(os.environ.get("CI"))

plt.ion()  # Enable interactive mode, so that plotting doesn't block

# Add fixtures used implicitly in all functions
pytestmark = pytest.mark.usefixtures("close_plots")


class Test_SlideShowPlot:
    """Test the SlideShowPlot by simulating input events."""

    @staticmethod
    def _frames_particles():
        particles = describe_lines(10, 10, 50, 50, 1, 1, seed=42)
        particles = add_properties(particles)
        frames = render_frames(particles, background=np.zeros((50, 50)))
        return list(frames), particles

    def test_only_frames(self):
        frames, _ = self._frames_particles()
        splot = ptvpy_plot.SlideShowPlot(frames)
        plt.show()

        assert splot.animation_state is True
        event = KeyEvent("name", splot.figure.canvas, key=" ")
        splot._on_key_press(event)
        assert splot.animation_state is False

        assert splot.frame_nr == 0

        splot.frame_nr = 2
        assert splot.slider.val == 2

        event = KeyEvent("name", splot.figure.canvas, key="right")
        splot._on_key_press(event)
        assert splot.frame_nr == 3
        event = KeyEvent("name", splot.figure.canvas, key="left")
        splot._on_key_press(event)
        assert splot.frame_nr == 2
        splot._advance_animation("any", "thing", "goes")
        assert splot.frame_nr == 3

    def test_with_particles(self):
        frames, particles = self._frames_particles()
        splot = ptvpy_plot.SlideShowPlot(frames, particles)
        plt.show()

        assert splot.animation_state is True
        event = KeyEvent("name", splot.figure.canvas, key=" ")
        splot._on_key_press(event)
        assert splot.animation_state is False

        assert splot.frame_nr == 0

        splot.frame_nr = 2
        assert splot.slider.val == 2

        event = KeyEvent("name", splot.figure.canvas, key="right")
        splot._on_key_press(event)
        assert splot.frame_nr == 3
        event = KeyEvent("name", splot.figure.canvas, key="left")
        splot._on_key_press(event)
        assert splot.frame_nr == 2
        splot._advance_animation("any", "thing", "goes")
        assert splot.frame_nr == 3

    def test_slider_overflow(self):
        """Check what happens if the slider moves of borders."""
        frames, particles = self._frames_particles()
        splot = ptvpy_plot.SlideShowPlot(frames, particles)
        plt.show()
        event = KeyEvent("name", splot.figure.canvas, key="left")
        splot._on_key_press(event)
        assert splot.frame_nr == splot.slider.valmax

        event = KeyEvent("name", splot.figure.canvas, key="right")
        splot._on_key_press(event)
        assert splot.frame_nr == 0

    def test_highlight_particle(self):
        """Check highlighting of a particle."""
        frames, particles = self._frames_particles()
        splot = ptvpy_plot.SlideShowPlot(frames, particles)
        plt.show()

        splot.frame_nr = 3
        particle = splot.particles_in_frame(splot.frame_nr).iloc[2, :]

        assert splot.annotation.get_visible() is False
        assert splot.trace_artist is None
        splot.highlight_particle(particle)
        splot.update_plot()
        assert splot.annotation.get_visible() is True
        assert splot.trace_artist is not None
        splot.remove_highlight()
        splot.update_plot()
        assert splot.annotation.get_visible() is False
        assert splot.trace_artist is None

        # Remove particle ID, the slide show should be able to display, even
        # if particles weren't linked yet
        del particle["particle"]
        assert splot.annotation.get_visible() is False
        splot.highlight_particle(particle)
        splot.update_plot()
        assert splot.annotation.get_visible() is True
        assert splot.trace_artist is None
        splot.remove_highlight()
        splot.update_plot()
        assert splot.annotation.get_visible() is False
        assert splot.trace_artist is None
