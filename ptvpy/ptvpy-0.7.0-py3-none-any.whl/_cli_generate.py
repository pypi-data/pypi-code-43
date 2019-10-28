"""Command-group `generate`."""


from functools import partial
from pathlib import Path

import click

from . import PtvPyError
from ._cli_utils import CliTimer, LazyImport


imageio = LazyImport("imageio")
np = LazyImport("numpy")
generate = LazyImport("..generate", package=__name__)


def _has_images(directory: Path) -> bool:
    """Check if `directory` contains files matching "image_*.tiff"."""
    try:
        next(directory.glob("image_*.tiff"))
    except StopIteration:
        return False
    else:
        return True


def _save_frames(timer, directory, frame_count, frames):
    """Save frames into given directory.

    Parameters
    ----------
    timer : CliTimer
        A timer to give visual feedback.
    directory : Path
        Directory to write to.
    frame_count: int
        The number of frames to write.
    frames : Iterable[numpy.ndarray]
        Iterable that yields the generated frames.
    """
    pad_width = int(np.ceil(np.log10(frame_count)))
    path_template = str(directory / f"image_{{:0>{pad_width}}}.tiff")
    with timer:
        for i, frame in enumerate(frames):
            # Ensure that allowed value range of storage format is not exceeded
            frame = frame.round().clip(0, 255).astype(np.uint8)
            with imageio.get_writer(path_template.format(i), mode="i") as writer:
                writer.append_data(frame, {"compress": 2})
            timer.update()


class ImagesExistError(PtvPyError, FileExistsError):
    """Directory already contains images matching the pattern for new images."""

    pass


def _generate_images(particle_factory, kwargs):
    """Generate and save new images.

    This functions handles the shared part of subcommands such as "ptvpy
    generate lines" and "ptvpy generate whirlpool".

    Parameters
    ----------
    particle_factory : callable
        A callable that takes no arguments and returns a DataFrame with the
        columns "frame", "particle", "x" and "y". E.g. as returned by
        :func:`~.generate.describe_lines`.
    kwargs : dict
        Command line arguments and options.
    """
    directory = Path(kwargs["directory"])
    directory.mkdir(parents=True, exist_ok=True)
    if _has_images(directory):
        raise ImagesExistError(
            "directory already contains files matching 'image_*.tiff'",
            hint="Delete these manually before generating new images here.",
        )

    seed = kwargs["seed"]
    click.echo(f"Using seed {seed}")

    with CliTimer("Preparing particle data"):
        particles = particle_factory()

        particles = generate.add_properties(
            particles,
            size=kwargs["particle_size"],
            brightness=kwargs["particle_brightness"],
            seed=seed,
        )

        particles["x"] = generate.jitter(particles["x"], kwargs["jitter"], seed=seed)
        particles["y"] = generate.jitter(particles["y"], kwargs["jitter"], seed=seed)

        if kwargs["helix"]:
            generate.add_helix_properties(particles, mode="slope", inplace=True)

            # Create a random offset for angles of each unique particle
            generator = np.random.RandomState(seed)
            offset = (
                generator.standard_normal(particles["particle"].nunique())
                * np.pi
                * 0.05
            )
            particles["angle"] += offset[particles["particle"]]
            particles["angle"].clip(-np.pi / 2, np.pi / 2, inplace=True)

            particles = generate.create_helix_pairs(particles)

        # Particles might be outside of the frame, remove before rendering
        keep = (
            (particles[["x", "y"]].min(axis=1) > 0)
            & (particles["x"] < kwargs["frame_size"][0])
            & (particles["y"] < kwargs["frame_size"][1])
        )
        particles = particles[keep]

        if kwargs["white_noise"]:
            background = generate.white_noise(
                shape=kwargs["frame_size"],
                mu=kwargs["white_noise"][0],
                variance=kwargs["white_noise"][1],
                seed=seed,
            )
        else:
            background = np.zeros(kwargs["frame_size"])

        frames = generate.render_frames(particles, background=background)

    timer = CliTimer("Generating frames", total=kwargs["frame_count"])
    _save_frames(timer, directory, kwargs["frame_count"], frames)

    file_path = directory / f"particles_{seed}.csv"
    particles.to_csv(file_path, index=False)
    click.echo(f"Saved source in '{file_path}'")


def _shared_generate_cli(func):
    """Add shared options and arguments to generate subcommands.

    Adds the arguments DIRECTORY and FRAME_COUNT as well as other common
    options.
    """
    # Arguments must be added in reverse order compared to usual order if
    # added as properties
    func = click.argument("frame_count", type=click.IntRange(min=1))(func)
    func = click.argument("directory", type=click.Path(file_okay=False))(func)

    func = click.option(
        "--jitter",
        metavar="FLOAT",
        type=click.FloatRange(min=0),
        default=0,
        help="Add noise drawn from a Gaussian distribution with the given "
        "variance to the particle positions.",
    )(func)
    func = click.option(
        "--white-noise",
        metavar="FLOAT FLOAT",
        type=click.FLOAT,
        nargs=2,
        help="Add white noise to each frame by specifying the mean value and "
        "variance of the noise. Pixel values are limited between 0 and 255.",
    )(func)
    func = click.option(
        "--particle-brightness",
        metavar="FLOAT FLOAT",
        type=click.FloatRange(min=0),
        nargs=2,
        default=(100, 10),
        help="Two values describing the average particle brightness a and its variance "
        "at the center. Pixel values are limited between 0 and 255. Default: 100 10",
    )(func)
    func = click.option(
        "--particle-size",
        metavar="FLOAT FLOAT",
        type=click.FloatRange(min=0),
        nargs=2,
        default=(5, 0.5),
        help="Two values describing the average particle size and its variance "
        "in pixels. The particle size corresponds to the variance of the gaussian "
        "blobs representing the particles. Default: 5 0.5",
    )(func)
    func = click.option(
        "--particle-count",
        metavar="INTEGER",
        type=click.IntRange(min=1),
        default=20,
        help="Number of particles in each frame. Default: 20",
    )(func)
    func = click.option(
        "--helix",
        is_flag=True,
        help="Will split each particle into a helix pair if given. The angle of the "
        "pair is a function of its position (angle ~ x - y).",
    )(func)
    func = click.option(
        "--seed",
        type=click.INT,
        default=lambda: np.random.randint(999_999),
        help="Seed the random number generator.",
    )(func)
    func = click.option(
        "--frame-size",
        metavar="INTEGER INTEGER",
        help="Size of the X and Y dimension of the created frames in pixels. "
        "Default: 200 200",
        type=click.IntRange(min=1),
        nargs=2,
        default=(200, 200),
    )(func)

    return func


@click.group(name="generate")
def generate_group():
    """Generate synthetic images.

    These commands will generate artificial images with particles moving in a
    defined pattern across the generated frames. The starting position, size
    and brightness of each particle are randomized while other parameters are
    configurable.

    Currently only the TIFF format is supported.
    """
    pass


@generate_group.command(name="lines")
@_shared_generate_cli
@click.option(
    "--velocity",
    metavar="FLOAT FLOAT",
    help="Velocity vector of the particles giving the step (X, Y) in pixels "
    "per frame. Default: 2 0",
    type=click.FloatRange(min=0),
    nargs=2,
    default=(2, 0),
)
def lines_command(**kwargs):
    """Generate particles moving along lines.

    Will create a FRAME_COUNT images in DIRECTORY matching "image_*.tiff". These images
    display particles moving along straight lines at the same velocity. The initial
    start position is randomized.
    The true particle data used to render the frames is saved in the same directory
    in a file named 'particles_XXX.csv' where XXX denotes the used seed.
    """
    particle_factory = partial(
        generate.describe_lines,
        frame_count=kwargs["frame_count"],
        particle_count=kwargs["particle_count"],
        x_max=kwargs["frame_size"][0],
        y_max=kwargs["frame_size"][1],
        x_vel=kwargs["velocity"][0],
        y_vel=kwargs["velocity"][1],
        wrap=True,
        seed=kwargs["seed"],
    )
    _generate_images(particle_factory, kwargs)


@generate_group.command(name="whirlpool")
@_shared_generate_cli
@click.option(
    "--angle-vel",
    metavar="FLOAT",
    type=click.FloatRange(min=0),
    default=0.3,
    help="Maximal angular velocity in radians per frame at the center of the "
    "whirlpool. The speed decreases linearly to zero for particles closer to "
    "the edge. Default: 0.3",
)
def whirlpool_command(**kwargs):
    """Generate particles moving in a whirlpool.

    Will create a FRAME_COUNT images in DIRECTORY matching "image_*.tiff". These images
    display particles moving inside a whirlpool. The initial start position is
    randomized (within a polar coordinate system). Particles closer to the whirlpools
    center move faster.
    The true particle data used to render the frames is saved in the same directory
    in a file named 'particles_XXX.csv' where XXX denotes the used seed.
    """
    radius = min(kwargs["frame_size"]) / 2

    particle_factory = partial(
        generate.describe_whirlpool,
        frame_count=kwargs["frame_count"],
        particle_count=kwargs["particle_count"],
        radius=radius,
        angle_vel=kwargs["angle_vel"],
        seed=kwargs["seed"],
    )
    _generate_images(particle_factory, kwargs)
