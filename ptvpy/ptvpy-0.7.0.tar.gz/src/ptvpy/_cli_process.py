"""Subcommand `process`."""


import click

from ._cli_utils import AddProfileDetection, CliTimer, LazyImport, print_summary


h5py = LazyImport("h5py")
multiprocessing_pool = LazyImport("multiprocessing.pool")
np = LazyImport("numpy")
pd = LazyImport("pandas")
trackpy = LazyImport("trackpy")
io = LazyImport("..io", package=__name__)
process = LazyImport("..process", package=__name__)


def _step_locate(profile, particle_shape=None):
    """Handle multi-threaded particle location.

    Parameters
    ----------
    profile : ChainedKeyMap
        Mapping like object containing the profile configuration.
    particle_shape : {"blob", "helix"}, optional
        If given, overwrites the profile value with the same name.

    Returns
    -------
    particles : pandas.DataFrame[frame, x, y, ...]
        Located particle positions and their properties.
    """
    if not particle_shape:
        particle_shape = profile["step_locate.particle_shape"]

    # Load frames
    loader = io.FrameLoader(
        pattern=profile["general.data_files"],
        slice_=slice(*profile["general.subset"][["start", "stop", "step"]]),
    )
    if profile["step_locate.remove_background"]:
        with CliTimer("Calculating background") as timer:
            loader.remove_background(profile["general.storage_file"])
            if loader.used_background_cache:
                timer.success_message = "done (used cache)"
    frames = loader.lazy_frame_sequence()

    # Prepare input for ThreadPool's worker function (_locate_worker)
    locate_kwargs = profile["step_locate.trackpy_locate"]
    if particle_shape == "helix":
        helix_kwargs = profile["step_locate.helix"]
    else:
        helix_kwargs = None

    def worker(i):
        # Make sure to load the frame only inside the worker as ThreadPool
        # will evaluate generators passed to its map-like methods at once.
        # So doing something like pool.imap(worker, enumerate(frames))
        # would load all frames into memory at once.
        particles = trackpy.locate(frames[i], **locate_kwargs)
        particles["frame"] = i
        if helix_kwargs:
            particles = process.find_helix_particles(particles, **helix_kwargs)
        return particles

    trackpy.quiet()  # Ensure that output of trackpy is suppressed
    particles = []
    with CliTimer("Locating particles", total=len(frames)) as timer:
        with multiprocessing_pool.ThreadPool(profile["step_locate.parallel"]) as pool:
            for results in pool.imap_unordered(worker, range(len(frames))):
                # TODO maybe, write directly to file, see "unlimited" keyword in
                # http://docs.h5py.org/en/latest/high/dataset.html#resizable-datasets
                particles.append(results)
                timer.update()
    particles = pd.concat(particles, ignore_index=True)
    return particles


def _step_link(profile, particles):
    """Handle particle linking.

    Parameters
    ----------
    profile : ChainedKeyMap
        Mapping like object containing the profile configuration.
    particles : pandas.DataFrame[frame, x, y, ...]
        Located particle positions and their properties.

    Returns
    -------
    linked_particles : pandas.DataFrame[frame, particle, x, y, ...]
        Linked particles, their positions and their properties.
    """
    trackpy.quiet()  # Ensure that output of trackpy is suppressed
    with CliTimer("Linking particles"):
        particles = trackpy.link(particles, **profile["step_link.trackpy_link"])
        particles = trackpy.filter_stubs(
            particles, **profile["step_link.trackpy_filter_stubs"]
        )
        particles.reset_index(drop=True, inplace=True)
    return particles


def _step_diff(profile, particles):
    """Handle calculation of particle velocities.

    Parameters
    ----------
    profile : ChainedKeyMap
        Mapping like object containing the profile configuration.
    particles : pandas.DataFrame[frame, particle, x, y, ...]
        Linked particles, their positions and their properties.

    Returns
    -------
    diffed_particles : pandas.DataFrame[frame, particle, x, y, dx, dy, v, ...]
        Velocities of the particles and other properties.
    """
    with CliTimer("Calculating velocities"):
        particles = process.xy_velocity(particles, profile["step_diff.diff_step"])
        particles = process.absolute_velocity(particles)
    return particles


@click.command(name="process")
@click.option(
    "--step",
    type=click.Choice(["locate", "link", "diff"]),
    multiple=True,
    help="Only do the given processing step(s). If not provided all steps given "
    "in the profile option will be used.",
)
@click.option(
    "--particle-shape",
    type=click.Choice(["blob", "helix"]),
    help="Overwrite the expected particle shape. If not provided the option "
    "given in the profile will be used.",
)
@AddProfileDetection()
def process_command(step, particle_shape, profile):
    """Process a data set.

    This command is controlled via a profile (see "ptvpy profile -h") that
    tells PtvPy where the data is stored and how to process it. Some profile
    options may be temporarily overwritten with the options listed below.

    \b
    Examples:
      ptvpy process
      ptvpy process --step locate --particle-shape helix
      ptvpy process --no-validation -p explicit_profile.toml
    """
    storage_path = profile["general.storage_file"]
    steps = step if step else profile["general.default_steps"]

    # Load previous results if they already exist
    with io.Storage(storage_path, "a") as file:
        if "particles" in file:
            particles = file.load_df("particles")
        elif "locate" in steps:
            particles = None
        else:
            error = io.NoParticleDataError(
                message=f"no particle data found in '{storage_path}'",
                hint="Generate data with 'locate' step before performing successive "
                "steps.",
            )
            raise error

    try:
        if "locate" in steps:
            particles = _step_locate(profile, particle_shape)
        if "link" in steps:
            particles = _step_link(profile, particles)
        if "diff" in steps:
            particles = _step_diff(profile, particles)

    finally:
        if particles is not None:
            with io.Storage(storage_path, "a") as file:
                dset = file.save_file(
                    str(profile.path), str(profile.path), overwrite=True
                )
                dset.attrs["comment"] = f"raw/binary copy of the file '{profile.path}'"
                dset = file.save_df("particles", particles, overwrite=True)
                dset.attrs[
                    "comment"
                ] = "measured and calculated properties of found particles"

    print_summary(particles)
