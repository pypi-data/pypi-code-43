"""Tools for plotting and visual inspection."""


import functools

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401, needed by scatter_plot_3d
import seaborn as sns


__all__ = [
    "SlideShowPlot",
    "heat_map",
    "histogram",
    "scatter_plot_2d",
    "scatter_plot_3d",
    "vector_field",
    "violin_plot",
]


def _suppress_autostart(plot):
    """Suppress autostart of animation in SlideShowPlot.

    A FuncAnimation auto-starts as soon as the GUI's event queue starts
    regardless of prior actions. Thus a sure way to pause the animation is to
    modify the behavior of the first 2 two actions (calls to `func`) by the
    animation itself. `func` is called once before the event queue starts. Thus
    we need to disable on the second call once the queue is actually running.

    Parameters
    ----------
    plot : SlideShowPlot
        The SlideShowPlot with the animation to suppress.

    Returns
    -------
    func : callable
        The frame function to pass to as the `func` argument to FuncAnimation's
        constructor.
    """
    # TODO Find a way to pause animation initially without this hack
    func = plot._advance_animation

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if wrapper.call_count < 2:
            plot.animation_state = False
            wrapper.call_count += 1
        else:
            return func(*args, **kwargs)

    wrapper.call_count = 0
    return wrapper


class SlideShowPlot:
    """Display annotated frames as a slide show.

    The animated slide show can be (un)paused with the space key. The slider
    can be controlled by dragging with the mouse or using the arrow keys.
    Clicking near a tracked particle will display its properties and path; use
    the left mouse button to unselect.

    Parameters
    ----------
    frames : sequence
        An index-able sized container object that returns each frame as an
        array.
    particles : pandas.DataFrame, optional
        Information on detected particles.
    autostart : bool, optional
        If True, the animation starts playing as soon as the GUI's event
        queue starts.

    Attributes
    ----------
    frame_nr : int
        Currently displayed frame and slider position.
    animation_state : bool
        Control the animation state. Setting this False will pause the
        animation. Works only after event queue of the GUI backend has started.
    """

    def __init__(self, frames, particles=None, autostart=False):
        if particles is None:
            particles = pd.DataFrame(columns=["frame", "particle", "x", "y"])

        # Data storing attributes
        self.frames = frames
        self.particles = particles
        self.highlighted_particle: pd.DataFrame = None

        # Init figure and axes
        self.figure = plt.figure()
        self.image_axes = self.figure.subplots()
        self.figure.subplots_adjust(bottom=0.2)
        self.slider_axes = self.figure.add_axes([0.25, 0.05, 0.52, 0.03])

        # Init slider
        self.slider = Slider(
            self.slider_axes,
            label="Frame",
            valmin=0,
            valmax=len(self.frames) - 1,
            valinit=0,
            valfmt="%i",
            valstep=1,
        )
        self.slider.on_changed(self.update_plot)

        # Init artists
        self.frame_artist = self.image_axes.imshow(
            self.frames[self.frame_nr], origin="lower", cmap="gray"
        )
        in_frame = self.particles_in_frame(self.frame_nr)
        self.particle_artist, = self.image_axes.plot(
            in_frame["x"], in_frame["y"], "r+", markersize=8, picker=True
        )
        # TODO: Investigate - Doesn't work when setting with plot method in
        #  which case pickradius is merily set to True
        self.particle_artist.set_pickradius(10)
        self.trace_artist: plt.Line2D = None

        # Init annotation, a popup displaying detailed information about a
        # picked article
        self.annotation = self.image_axes.annotate(
            "",
            xy=(0, 0),
            xytext=(-20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->", color="yellow"),
        )
        self.annotation.set_visible(False)

        # Init animation
        self._animation_state = True
        func = self._advance_animation if autostart else _suppress_autostart(self)
        self.animation = FuncAnimation(self.figure, func=func)

        # Connect slots
        self.figure.canvas.mpl_connect("key_press_event", self._on_key_press)
        self.figure.canvas.mpl_connect("pick_event", self._on_pick)
        self.figure.canvas.mpl_connect("button_press_event", self._on_button_press)
        self.figure.canvas.mpl_connect("button_release_event", self._on_button_release)
        self._button_3_start_pos = None  # Used in button event slots

    @property
    def frame_nr(self):
        return int(self.slider.val)

    @frame_nr.setter
    def frame_nr(self, nr):
        nr = int(nr % (self.slider.valmax + 1))
        self.slider.set_val(nr)

    @property
    def animation_state(self):
        return self._animation_state

    @animation_state.setter
    def animation_state(self, state):
        if state is True:
            self.animation.event_source.start()
        elif state is False:
            self.animation.event_source.stop()
        else:
            raise TypeError("expects a boolean")
        self._animation_state = state

    def particles_in_frame(self, nr):
        """Select particle data from a single frame."""
        return self.particles[self.particles["frame"] == nr]

    def update_plot(self, *_):
        """Redraw the plot to match the current frame number."""
        self.frame_artist.set_data(self.frames[self.frame_nr])
        particles = self.particles_in_frame(self.frame_nr)
        self.particle_artist.set_data(particles["x"], particles["y"])

        if self.highlighted_particle is not None:
            # Update annotation if particle is currently visible
            nr = self.highlighted_particle["particle"].iloc[0]
            particle = particles[particles["particle"] == nr].squeeze()
            if particle.size > 0:
                self._update_particle_annotation(particle)

        self.figure.canvas.draw_idle()

    def highlight_particle(self, particle):
        """Show path and annotation of a particle over multiple frames.

        Parameters
        ----------
        particle : pandas.DataFrame[x, y, [particle, ...]]
            A DataFrame with a particle's position and optionally ID.
        """
        self.remove_highlight()

        if "particle" in particle:
            # If ID was provided show the particles trajectory
            nr = particle["particle"]
            self.highlighted_particle = self.particles[self.particles["particle"] == nr]
            self.trace_artist, = self.image_axes.plot(
                self.highlighted_particle["x"],
                self.highlighted_particle["y"],
                "y--",
                zorder=1,
            )
            particle = self.highlighted_particle[
                self.highlighted_particle["frame"] == self.frame_nr
            ].squeeze()  # Ensure that it's a Series

        self._update_particle_annotation(particle)
        self.annotation.set_visible(True)
        self.figure.canvas.draw_idle()

    def remove_highlight(self):
        """Remove path and annotation of a particle from the plot."""
        if self.trace_artist is not None:
            self.trace_artist.remove()
            self.trace_artist = None
        self.highlighted_particle = None
        self.annotation.set_visible(False)
        self.figure.canvas.draw_idle()

    def _update_particle_annotation(self, particle):
        """Update position and text of annotation."""
        self.annotation.xy = (particle["x"], particle["y"])
        self.annotation.set_text(
            "\n".join(f"{key} = {value:g}" for key, value in particle.items())
        )

    def _advance_animation(self, *_):
        """Advance animation (slot for animation)."""
        self.frame_nr += 1

    def _on_key_press(self, event):
        """Deal with key press events."""
        if event.key == "right":
            self.frame_nr += 1
        elif event.key == "left":
            self.frame_nr -= 1
        elif event.key == " ":
            self.animation_state = not self.animation_state  # Toggle

    def _on_pick(self, event):
        """Deal with pick events (selection of artist elements)."""
        if event.artist == self.particle_artist:
            index = event.ind[0]
            particle = self.particles_in_frame(self.frame_nr).iloc[index, :]
            self.highlight_particle(particle)

    def _on_button_press(self, event):
        """Deal with mouse button press events."""
        if event.button == 3:
            self._button_3_start_pos = (event.x, event.y)

    def _on_button_release(self, event):
        """Deal with mouse button release events."""
        if event.button == 3:
            if self._button_3_start_pos == (event.x, event.y):
                # Don't remove when mouse was dragged while pressed, this
                # allows proper use of the pan and zoom modes
                self.remove_highlight()


def heat_map(x, y, z, *, data=None, fig_ax=None):
    """Plot variable as a color-coded 2D heatmap.

    Parameters
    ----------
    x, y, z : str or ndarray
        Either 1D arrays or keys for `data`. x and y are interpreted as
        coordinates of the regular sampled scalar field z.
    data : pandas.DataFrame, optional, columns (x, y, z)
        Optional DataFrame with columns matching the 4 variables above.
    fig_ax : (matplotlib.Figure, maptlotlib.Axes), optional
        The figure and axes used to create the plot. If not provided new ones
        will be created.

    Returns
    -------
    figure : matplotlib.Figure
        The created figure.
    axes : matplotlib.Axes
        The created axes.
    """
    if data is not None:
        x = data.get(x, x)
        y = data.get(y, y)
        z = data.get(z, z)

    data = pd.DataFrame({"x": x, "y": y, "z": z})
    z_grid = data.pivot(index="y", columns="x").values
    x_grid = np.asarray(x).reshape(z_grid.shape)
    y_grid = np.asarray(y).reshape(z_grid.shape)

    figure, axes = plt.subplots() if fig_ax is None else fig_ax
    caxes = axes.pcolormesh(x_grid, y_grid, z_grid, cmap="magma")
    cbar = figure.colorbar(caxes)
    cbar.outline.set_linewidth(0)

    if hasattr(z, "name"):
        cbar.ax.set_ylabel(z.name)
    if hasattr(x, "name"):
        axes.set_xlabel(x.name)
    if hasattr(y, "name"):
        axes.set_ylabel(y.name)

    sns.despine(ax=axes)

    figure.set_tight_layout(True)
    return figure, axes


def histogram(*variables, data=None, log=True, fig_ax=None):
    """Create a histogram of `x`.

    Parameters
    ----------
    *variables : iterable[str or ndarray]
        Either 1D arrays or keys for `data`.
    data : pandas.DataFrame, optional
        Optional DataFrame with columns matching the keys in `variables`.
    log : bool, optional
        Use logarithmic scale for y-axis showing the size of each bin.
    fig_ax : (matplotlib.Figure, maptlotlib.Axes), optional
        The figure and axes used to create the plot. If not provided new ones
        will be created.

    Returns
    -------
    figure : matplotlib.figure.Figure
        Figure used to draw.
    axes : matplotlib.axes.Axes
        Axes used for plotting.
    """
    if data is not None:
        variables = [(v, data.get(v, v)) for v in variables]

    figure, axes = plt.subplots() if fig_ax is None else fig_ax
    axes.grid(True, alpha=0.5)

    for label, v in variables:
        v = v.ravel()
        v = v[~np.isnan(v)]
        sns.distplot(
            v, label=label, hist=True, kde=True, ax=axes, hist_kws={"log": log}
        )

    if len(variables) > 1:
        axes.legend()
        axes.set_xlabel("")

    return figure, axes


def scatter_plot_2d(x, y, c=None, *, data=None, fig_ax=None):
    """Plot regression plot between two variables.

    Parameters
    ----------
    x, y: str or ndarray
        Either 1D arrays or keys for `data`.
    c : str or ndarray, optional
        Either 1D array or key for `data`. Used as the basis for coloring the
        scatter points using a colormap.
    data : pandas.DataFrame, optional, columns (x, y)
        Optional DataFrame with columns matching the 4 variables above.
    fig_ax : (matplotlib.Figure, maptlotlib.Axes), optional
        The figure and axes used to create the plot. If not provided new ones
        will be created.

    Returns
    -------
    figure : matplotlib.Figure
        The created figure.
    axes : matplotlib.Axes
        The created axes.
    """
    reg_line_color = None
    if data is not None:
        x = data.get(x, x)
        y = data.get(y, y)
        c = data.get(c, c)

    figure, axes = plt.subplots() if fig_ax is None else fig_ax
    axes.grid(True, alpha=0.5)

    points = axes.scatter(x, y, c=c, cmap="magma", s=10)
    if c is not None:
        cbar = figure.colorbar(points)
        cbar.outline.set_linewidth(0)
        reg_line_color = "gray"

    # Postpone setting alpha to avoid pale colors in colorbar
    points.set_alpha(0.2)

    sns.regplot(
        x, y, scatter=False, truncate=True, order=6, ax=axes, color=reg_line_color
    )

    return figure, axes


def scatter_plot_3d(x, y, z, c=None, *, data=None):
    """Create a scatter plot with 3 dimensions.

    Parameters
    ----------
    x, y, z : str or ndarray
        Either 1D arrays or keys for `data`. `x` and `y` are interpreted as
        coordinates of the regular sampled scalar field `z`.
    c : str or ndarray, optional
        Either 1D array or key for `data`. Used as the basis for coloring the
        scatter points using a colormap.
    data : pandas.DataFrame, optional
        Optional DataFrame with columns matching the given variables above.

    Returns
    -------
    figure : matplotlib.Figure
        The created figure.
    axes : matplotlib.Axes
        The created axes.
    """
    if data is not None:
        x = data.get(x, x)
        y = data.get(y, y)
        z = data.get(z, z)
        if c is not None:
            c = data.get(c, c)

    figure = plt.figure()
    axes = figure.add_subplot(111, projection="3d")
    points = axes.scatter(xs=x, ys=y, zs=z, c=c, cmap="magma", depthshade=False)
    if c is not None:
        cbar = figure.colorbar(points)
        cbar.outline.set_linewidth(0)

    # Postpone setting alpha to avoid pale colors in colorbar
    points.set_alpha(0.2)

    # Set label names
    if hasattr(c, "name"):
        cbar.set_label(c.name)
    if hasattr(x, "name"):
        axes.set_xlabel(x.name)
    if hasattr(y, "name"):
        axes.set_ylabel(y.name)
    if hasattr(z, "name"):
        axes.set_zlabel(z.name)

    figure.set_tight_layout(True)
    return figure, axes


def vector_field(x, y, dx, dy, *, data=None, heatmap=True, fig_ax=None):
    """Plot two variables as a 2D vector field.

    Parameters
    ----------
    x, y, dx, dy : str or ndarray
        Either 1D arrays or column names for `data`. `x` and `y` are interpreted
        as coordinates of the two regular sampled scalar fields `dx` (in `x`
        direction) and `dy` (in `y` direction).
        of the vector field.
    data : pandas.DataFrame, optional, columns (x, y, dx, dy)
        Optional DataFrame with columns matching the 4 variables above.
    heatmap : bool, optional
        If true, a map of the absolute value of each arrow (`dx`, `dy`) is used
        to plot a heatmap in the background.
    fig_ax : (matplotlib.Figure, maptlotlib.Axes), optional
        The figure and axes used to create the plot. If not provided new ones
        will be created.

    Returns
    -------
    figure : matplotlib.Figure
        The created figure.
    axes : matplotlib.Axes
        The created axes.
    """
    if data is not None:
        x = data.get(x, x)
        y = data.get(y, y)
        dx = data.get(dx, dx)
        dy = data.get(dy, dy)

    dxy = np.sqrt(dx ** 2 + dy ** 2)
    if hasattr(dx, "name") and hasattr(dy, "name"):
        # Set name so that is recognized as the label for the colorbar
        setattr(dxy, "name", f"|({dx.name}, {dy.name})|")

    figure, axes = plt.subplots() if fig_ax is None else fig_ax

    if heatmap:
        heat_map(x, y, dxy, fig_ax=(figure, axes))

    axes.quiver(x, y, dx, dy, dxy, cmap="binary", units="xy")

    if hasattr(x, "name"):
        axes.set_xlabel(x.name)
    if hasattr(y, "name"):
        axes.set_ylabel(y.name)
    if hasattr(dx, "name"):
        axes.set_xlabel("{} [{}]".format(axes.get_xlabel(), dx.name))
    if hasattr(dy, "name"):
        axes.set_ylabel("{} [{}]".format(axes.get_ylabel(), dy.name))

    if not heatmap:
        # Only show grid when there is no heatmap in the background
        axes.grid(True, alpha=0.5)

    return figure, axes


def violin_plot(*variables, data=None, fig_ax=None):
    """

    Parameters
    ----------
    *variables : iterable[str or ndarray]
        Either 1D arrays or keys for `data`.
    data : pandas.DataFrame, optional
        Optional DataFrame with columns matching the keys in `variables`.
    fig_ax : (matplotlib.Figure, maptlotlib.Axes), optional
        The figure and axes used to create the plot. If not provided new ones
        will be created.

    Returns
    -------
    figure : matplotlib.figure.Figure
        Figure used to draw.
    axes : matplotlib.axes.Axes
        Axes used for plotting.
    """
    if data is not None:
        data = data[list(variables)]
    else:
        data = pd.DataFrame(columns=range(len(variables)), data=variables)

    figure, axes = plt.subplots() if fig_ax is None else fig_ax
    axes.grid(True, alpha=0.5)
    sns.violinplot(data=data, ax=axes, scale="count", inner="quartile")

    return figure, axes
