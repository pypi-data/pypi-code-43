"""Command-group `view` with subcommands."""


from pathlib import Path

import click

from ._cli_utils import AddProfileDetection, CliTimer, LazyImport, print_summary


pd = LazyImport("pandas")
plt = LazyImport("matplotlib.pyplot")
trackpy = LazyImport("trackpy")
io = LazyImport("..io", package=__name__)
plot = LazyImport("..plot", package=__name__)
process = LazyImport("..process", package=__name__)


#: Share profile between view's subcommands. The decorators attribute "profile" is
#: cleared in :func:`~.view_resultcallback`.
_add_profile_detection = AddProfileDetection(remember=True)


@click.group(name="view", chain=True)
def view_group():
    """Inspect and plot data.

    The subcommands of this group can be chained and will share the profile
    loaded / detected by the first subcommand.

    \b
    Examples:
      ptvpy view histogram -h
      ptvpy view vector x v dx dy
      ptvpy view scatter3d x y v slideshow violin v
      ptvpy view summary -p explicit_profile.toml
    """
    pass


@view_group.resultcallback()
def _view_resultcallback(results, **_):
    """Show plots after chain of subcommands has run.

    Called after :func:`view_group` and its (chained) subcommands complete.
    """
    try:
        if any(results):
            click.echo("\nShowing plot(s)...")
            plt.show()
    finally:
        # Reset shared profile after chain is complete, we DON'T want to share it
        # between separate invokations (e.g. through tests or an interactive prompt).
        _add_profile_detection.reset()


def _load_particles(profile):
    """Load particle data for the given `profile`.

    Parameters
    ----------
    profile : ptvpy._profile.Profile
        Profile pointing to the file with particle data.

    Returns
    -------
    particles : pandas.DataFrame
        Particle data.

    Raises
    ------
    FileNotFoundError
    """
    path = Path(profile["general.storage_file"])
    if not path.is_file():
        error = FileNotFoundError(f"'{path}' does not exist")
        error.hint = "Generate data with 'ptvpy process' beforehand."
        raise error
    with io.Storage(path, "r") as file:
        if "particles" not in file:
            error = io.NoParticleDataError(f"no particle data found in '{path}'")
            error.hint = "Generate data with 'ptvpy process' beforehand."
            raise error
        return file.load_df("particles")


@view_group.command(name="background")
@_add_profile_detection
def background_command(profile):
    """Plot average per pixel for used frames."""
    with CliTimer("Preparing background"):
        loader = io.FrameLoader(
            pattern=profile["general.data_files"],
            slice_=slice(*profile["general.subset"][["start", "stop", "step"]]),
        )
        background = loader.load_background(profile["general.storage_file"])
        figure, axes = plt.subplots()
        axes.imshow(background, origin="lower", cmap="gray")
        figure.canvas.set_window_title("PtvPy: Background")
        return figure


@view_group.command(name="heatmap")
@click.argument("x", type=click.STRING)
@click.argument("y", type=click.STRING)
@click.argument("z", type=click.STRING)
@click.option(
    "--extrapolate",
    help="Extrapolate values outside convex hull of the data points.",
    is_flag=True,
)
@_add_profile_detection
def heatmap_command(profile, x, y, z, extrapolate):
    """Plot heat map of Z in X & Y.

    \b
    ptvpy view heatmap x y v
    ptvpy view heatmap --extrapolate x y v
    """
    with CliTimer("Preparing map"):
        particle_data = _load_particles(profile)
        out = process.scatter_to_regular(
            [x, y, z], data=particle_data, extrapolate=extrapolate
        )
        figure, _ = plot.heat_map(x, y, z, data=out)
        figure.canvas.set_window_title(f"PtvPy: Map {[x, y, z]}")
        return figure


@view_group.command(name="histogram")
@click.argument("x", type=click.STRING, nargs=-1)
@click.option("--log", is_flag=True, help="Use logarithmic scale for quantities.")
@_add_profile_detection
def histogram_command(profile, x, log):
    """Plot histogram of X.

    \b
    Examples:
      ptvpy view histogram mass
      ptvpy view histogram --log dx dy
    """
    with CliTimer("Preparing histogram"):
        particles = _load_particles(profile)
        figure, _ = plot.histogram(*x, data=particles, log=log)
        figure.canvas.set_window_title(f"PtvPy: Histogram {x}")
        return figure


@view_group.command(name="scatter2d")
@click.argument("x", type=click.STRING)
@click.argument("y", type=click.STRING)
@click.option(
    "--color", help="Use variable to color the data points.", type=click.STRING
)
@_add_profile_detection
def scatter2d_command(profile, x, y, color):
    """Show scatter plot between X and Y.

    \b
    Examples:
      ptvpy view scatter2d mass size
      ptvpy view scatter2d --color v x y
    """
    with CliTimer("Preparing scatter plot (2D)"):
        particle = _load_particles(profile)
        figure, _ = plot.scatter_plot_2d(x, y, c=color, data=particle)
        figure.canvas.set_window_title(f"PtvPy: Scatter plot in 2D {[x, y]}")
        return figure


@view_group.command(name="scatter3d")
@click.argument("x", type=click.STRING)
@click.argument("y", type=click.STRING)
@click.argument("z", type=click.STRING)
@click.option(
    "--color", help="Use variable to color the data points.", type=click.STRING
)
@_add_profile_detection
def scatter3d_command(profile, x, y, z, color):
    """Show scatter plot between X, Y and Z.

    \b
    Examples:
      ptvpy view scatter3d x y v
      ptvpy view scatter3d --color mass x y v
    """
    with CliTimer("Preparing scatter plot (3D)"):
        particle_data = _load_particles(profile)
        figure, _ = plot.scatter_plot_3d(x, y, z, color, data=particle_data)
        title = f"PtvPy: Scatter plot in 3D {[x, y, z]}"
        figure.canvas.set_window_title(title)
        return figure


@view_group.command(name="slideshow")
@click.option(
    "--autostart", is_flag=True, help="Autostart animation of the slide show."
)
@click.option("--no-annotation", is_flag=True, help="Don't display annotations.")
@_add_profile_detection
def slideshow_command(profile, autostart, no_annotation):
    """Show slide show of annotated frames.

    The animated slide show can be (un)paused with the space key. The slider
    can be controlled by dragging with the mouse or using the arrow keys.
    Clicking near a tracked particle will display its properties and path; use
    the left mouse button to unselect.

    \b
    Examples:
      ptvpy view slideshow
      ptvpy view slideshow --autostart --no-annotation
    """
    with CliTimer("Preparing slideshow"):
        if no_annotation:
            particles = None
        else:
            try:
                particles = _load_particles(profile)
            except (FileNotFoundError, io.NoParticleDataError):
                particles = None
        loader = io.FrameLoader(
            pattern=profile["general.data_files"],
            slice_=slice(*profile["general.subset"][["start", "stop", "step"]]),
        )
        if profile["step_locate.remove_background"]:
            loader.remove_background(profile["general.storage_file"])
        frames = loader.lazy_frame_sequence()
        slide_show_plot = plot.SlideShowPlot(frames, particles, autostart)
        slide_show_plot.figure.canvas.set_window_title("PtvPy: Slide show")
        return slide_show_plot


@view_group.command(name="subpixel")
@_add_profile_detection
def subpixel_command(profile):
    """Show fractional parts of coordinates.

    Helpful to detect a bias in particle positions towards integer values due
    to peak-locking.
    """
    with CliTimer("Preparing subpixel plot"):
        particle_data = _load_particles(profile)
        trackpy.subpx_bias(particle_data)
        return True


@view_group.command(name="summary")
@click.option(
    "--all",
    "show_all",
    is_flag=True,
    help="Summarize every measured/calculated quantity.",
)
@_add_profile_detection
def summary_command(profile, show_all):
    """Print summarizing statistics.

    \b
    Examples:
      ptvpy view summary --all
    """
    print_summary(_load_particles(profile), show_all)


@view_group.command(name="trajectories")
@click.option(
    "--names",
    default=["x", "y"],
    help="Names of the first and second coordinate.",
    nargs=2,
    type=click.STRING,
)
@_add_profile_detection
def trajectories_command(profile, names):
    """Plot trajectories of detected particles."""
    names = list(names)
    with CliTimer("Preparing trajectory plot"):
        particle_data = _load_particles(profile)
        figure, ax_traj = plt.subplots()
        trackpy.plot_traj(particle_data, ax=ax_traj, pos_columns=names)
        figure.canvas.set_window_title("PtvPy: Particle trajectories")
        return figure


@view_group.command(name="vector")
@click.argument("x", type=click.STRING)
@click.argument("y", type=click.STRING)
@click.argument("dx", type=click.STRING)
@click.argument("dy", type=click.STRING)
@click.option(
    "--heatmap",
    help="Plot heatmap of absolute value each arrow (dx, dy) in the background.",
    is_flag=True,
)
@click.option(
    "--extrapolate",
    help="Extrapolate values outside convex hull of the data points.",
    is_flag=True,
)
@_add_profile_detection
def vector_command(profile, x, y, dx, dy, heatmap, extrapolate):
    """Plot vector field of DX & DY in X & Y.

    \b
    Examples:
      ptvpy view vector dx dy x y
      ptvpy view vector --heatmap --extrapolate dx dy x y
    """
    with CliTimer("Preparing vector field"):
        particle_data = _load_particles(profile)
        u_out = process.scatter_to_regular(
            (x, y, dx), data=particle_data, extrapolate=extrapolate
        )
        v_out = process.scatter_to_regular(
            (x, y, dy), data=particle_data, extrapolate=extrapolate
        )
        data = pd.merge(u_out, v_out, how="outer")
        figure, _ = plot.vector_field(x, y, dx, dy, data=data, heatmap=heatmap)
        figure.canvas.set_window_title(f"PtvPy: Vector field {[dx, dy]} in {[x, y]}")
        return figure


@view_group.command(name="violin")
@click.argument("x", type=click.STRING, nargs=-1)
@_add_profile_detection
def violin_command(profile, x):
    """Show violin plot of X.

    \b
    Examples:
      ptvpy view violin mass
      ptvpy view violin dx dy
    """
    with CliTimer("Preparing violin plot"):
        particles = _load_particles(profile)
        figure, _ = plot.violin_plot(*x, data=particles)
        figure.canvas.set_window_title(f"PtvPy: Violin plot {x}")
        return figure
