"""Tools to generate synthetic data."""


from collections.abc import Iterable

import numpy as np
import pandas as pd
from numba import jit


__all__ = [
    "describe_lines",
    "describe_whirlpool",
    "add_properties",
    "add_helix_properties",
    "create_helix_pairs",
    "jitter",
    "overlay_gaussian_blob",
    "white_noise",
    "render_frames",
]


def describe_lines(
    frame_count, particle_count, x_max, y_max, x_vel, y_vel, *, wrap=True, seed=None
):
    """Describe coordinates of particles inside a uniform current.

    Will create a DataFrame describing particles floating inside a uniform
    current. While their starting position is randomized all particles share
    the same speed.

    Parameters
    ----------
    frame_count : int
        Number of frames to describe.
    particle_count : int
        Number of particles to describe.
    x_max, y_max : int, float
        Defines the area with the particles randomized start position.
    x_vel, y_vel : int, float
        Speed of particles in cartesian coordinates per frame.
    wrap : bool, optional
        Depending on their start position and velocity, particles may leave the
        area defined by (`x_max`, `y_max`) and the coordinate origin. If
        wrapping is enabled these particles won't leave this area and will
        reappear on the opposite site.
    seed : int, optional
        Used as a seed for the randomness generator. Using the same value for
        `seed` (and all other parameters) will result in the same output.

    Returns
    -------
    particles : pandas.DataFrame[frame, particle, x, y]
        A DataFrame with cartesian coordinates for each particle for each
        frame.

    Examples
    --------
    >>> describe_lines(frame_count=4, particle_count=1, x_max=100, y_max=100,
    ...                x_vel=10, y_vel=20, seed=1)
       frame  particle        x          y
    0      0         0  41.7022  72.032449
    1      1         0  51.7022  92.032449
    2      2         0  61.7022  12.032449
    3      3         0  71.7022  32.032449
    """
    generator = np.random.RandomState(seed)
    x_start = generator.random_sample(particle_count) * x_max
    y_start = generator.random_sample(particle_count) * y_max

    frame_nrs = np.arange(frame_count)
    particle_nrs = np.arange(particle_count)

    # Evaluate all frame - particle combinations
    frame_nrs, particle_nrs = np.meshgrid(frame_nrs, particle_nrs)

    x = x_start[particle_nrs] + frame_nrs * x_vel
    y = y_start[particle_nrs] + frame_nrs * y_vel

    if wrap is True:
        x %= x_max
        y %= y_max

    particles = pd.DataFrame(
        {
            "frame": frame_nrs.ravel(),
            "particle": particle_nrs.ravel(),
            "x": x.ravel(),
            "y": y.ravel(),
        }
    )
    return particles


def describe_whirlpool(frame_count, particle_count, radius, angle_vel, *, seed=None):
    """Describe coordinates of particles inside a whirlpool.

    Will create a DataFrame describing particles floating inside a whirlpool.
    The particles angular velocity is highest at the center and decreases linearly
    with the radius. The initial start position (radius, angle) of particles is
    randomized.

    Parameters
    ----------
    frame_count : int
        Number of frames to describe.
    particle_count : int
        Number of particles to describe.
    radius : int, float
        Radius of the whirlpool in pixels.
    angle_vel : int, float
        Maximum angular velocity in radians per frame at the center of the
        whirlpool.
    seed : int, optional
        Used as a seed for the randomness generator. Using the same value for
        `seed` (and all other parameters) will result in the same output.

    Returns
    -------
    particles : pandas.DataFrame[frame, particle, x, y]
        A DataFrame with cartesian coordinates for each particle for each
        frame.

    Examples
    --------
    >>> describe_whirlpool(frame_count=2, particle_count=2, radius=100,
    ...                    angle_vel=1, seed=1)
       frame  particle           x           y
    0      0         0  182.609243  100.059366
    1      1         0  181.352909  114.352519
    2      0         1   84.463170  145.535623
    3      1         1   63.927131  131.837622
    """
    # Prepare random starting positions
    generator = np.random.RandomState(seed)
    radii = (1 - generator.random_sample(particle_count) ** 2) * radius
    phases = generator.random_sample(particle_count) * 2 * np.pi
    velocities = angle_vel * (1 - radii / radius)
    # Prepare remaining input for function
    frame_nrs = np.arange(frame_count)
    particle_nrs = np.arange(particle_count)

    # Evaluate all frame - particle combinations
    frame_nrs, particle_nrs = np.meshgrid(frame_nrs, particle_nrs)

    arg = frame_nrs * velocities[particle_nrs] + phases[particle_nrs]
    # Coordinates should be positive: + radius
    x = radii[particle_nrs] * np.cos(arg) + radius
    y = radii[particle_nrs] * np.sin(arg) + radius

    particles = pd.DataFrame(
        {
            "frame": frame_nrs.ravel(),
            "particle": particle_nrs.ravel(),
            "x": x.ravel(),
            "y": y.ravel(),
        }
    )
    return particles


# TODO def describe_brownian_motion()
# https://scipy.github.io/old-wiki/pages/Cookbook/BrownianMotion
# https://scipy-cookbook.readthedocs.io/items/BrownianMotion.html


def add_properties(
    particles, *, size=(2, 0.2), brightness=(100, 10), seed=None, inplace=False
):
    """Add columns describing particles size and brightness.

    Parameters
    ----------
    particles : pandas.DataFrame[particle, ...]
        A DataFrame with a row "particle" containing integers.
    size : tuple(number, number), optional
        Two values describing the average particle size and its variance.
        The particle size corresponds to the variance of the gaussian blobs
        representing the particles.
    brightness : tuple(number, number), optional
        Two values describing the average particle brightness and its variance.
    seed : int, optional
        Used as a seed for the randomness generator. Using the same value for
        `seed` (and all other parameters) will result in the same output.
    inplace : bool, optional
        Modify `df` inplace or create a copy instead.

    Returns
    -------
    appended_particles : pandas.DataFrame[particle, size, brightness, ...]
        A copy of `particles` with two new columns describing the particles
        size and brightness.

    Notes
    -----
    The brightness and size of particles are dependent. Thus the same random
    seed is used to calculate their normal distributions. Both quantities
    are clipped below 0.

    Examples
    --------
    >>> particles = pd.DataFrame({"particle": [0, 1, 2, 3]})
    >>> add_properties(particles, seed=42)
       particle      size  brightness
    0         0  2.099343  104.967142
    1         1  1.972347   98.617357
    2         2  2.129538  106.476885
    3         3  2.304606  115.230299
    """
    if not inplace:
        particles = particles.copy()

    generator = np.random.RandomState(seed)
    particle_count = len(particles["particle"].unique())
    seed_vector = generator.standard_normal(particle_count)

    size = seed_vector * size[1] + size[0]
    brightness = seed_vector * brightness[1] + brightness[0]
    size[size < 0] = 0
    brightness[brightness < 0] = 0

    particles["size"] = size[particles["particle"]]
    particles["brightness"] = brightness[particles["particle"]]

    return particles


def add_helix_properties(particles, mode, *, inplace=False):
    r"""Add angle and pair distance as columns for each particle.

    Will assign each particle an angle and a distance which is based on on
    other properties of the particle. The distance is 2 times the median
    particle size while the angle is based on the position and scaled to the
    interval :math:`[-\frac{\pi}{2}, \frac{\pi}{2}]`.

    Parameters
    ----------
    particles : pandas.DataFrame[particle, x, y, size, ...]
        A DataFrame with a row "particle" containing integers.
    mode : {"slope"}
        A mode defining how the angle and pair distance are calculated.
        Available are:

            * ``slope`` - Angle will be a linear function of the position:
              :math:`f(x, y) \propto x - y`.

    inplace : bool, optional
        Modify `particles` inplace or create a copy instead.

    Returns
    -------
    particles : pandas.DataFrame[particle, x, y, size, angle, pair_distance, ...]
        Same as `particles` but with the additional columns "angle" and
        "pair_distance".

    Examples
    --------
    >>> particles = pd.DataFrame(
    ...     [[1, 20, 30, 3], [2, 25, 30, 4]],
    ...     columns=["particle", "x", "y", "size"]
    ... )
    >>> add_helix_properties(particles, mode="slope")
       particle   x   y  size     angle  pair_distance
    0         1  20  30     3 -1.570796            7.0
    1         2  25  30     4  1.570796            7.0
    """
    if not inplace:
        particles = particles.copy()

    if mode == "slope":
        angle = particles["x"] - particles["y"]
        # Rescale to interval [-pi/2, pi/2]
        angle -= angle.min()
        angle *= np.pi / angle.max()
        angle -= np.pi / 2
        particles["angle"] = angle
    else:
        raise ValueError(f"unknown mode: {mode}")

    particles["angle"].clip(-np.pi / 2, np.pi / 2, inplace=True)
    particles["pair_distance"] = particles["size"].median() * 2

    return particles


def create_helix_pairs(particles):
    """Separate particles with angle and distance into helix pairs.

    Parameters
    ----------
    particles : pandas.DataFrame[x, y, angle, pair_distance, ...]
        A DataFrame with the specified columns.

    Returns
    -------
    unpaired_particles : pandas.DataFrame[x, y, ...]
        A new DataFrame where each row in `particles` was split into two
        identical rows except for the columns "x" and "y" whose values where
        shifted separately depending on "angle" and "pair_distance". Assuming
        `particles` has the shape (m, n) then this DataFrame has the shape
        (2m, n-2).

    Examples
    --------
    >>> particles = pd.DataFrame(
    ...     [[1, 20, 100, 0.79, 10]],
    ...     columns=["particle", "x", "y", "angle", "pair_distance"]
    ... )
    >>> create_helix_pairs(particles)
       particle          x           y  angle  pair_distance
    0         1  16.480773   96.448234   0.79             10
    0         1  23.519227  103.551766   0.79             10
    """
    particles_a = particles.copy()
    particles_b = particles_a.copy()

    # Calculate the pair distance per coordinate
    x_distance = particles["pair_distance"] * np.cos(particles["angle"])
    y_distance = particles["pair_distance"] * np.sin(particles["angle"])

    # Shift particles in A / B in negative / positive direction
    particles_a["x"] -= x_distance / 2
    particles_a["y"] -= y_distance / 2
    particles_b["x"] += x_distance / 2
    particles_b["y"] += y_distance / 2

    return pd.concat([particles_a, particles_b])


def jitter(x, variance, *, clip=None, seed=None, inplace=False):
    """Add Gaussian noise to an array.

    Parameters
    ----------
    x : numpy.ndarray
        Values to jitter.
    variance : int or float
        Scale the distribution with which the noise is generated.
    clip : (float, float), optional
        Limit the values of `y` to the given range [min, max].
    seed : int, optional
        Used as a seed for the randomness generator. Using the same value for
        `seed` (and all other parameters) will result in the same output.
    inplace : bool, optional
        Modifies `x` inplace if True. `x` must be a floating type.

    Returns
    -------
    y : numpy.ndarray
        The sum of `x` and the generated noise.

    Raises
    ------
    ValueError
        If a jittered column doesn't contain a subdtype of float.

    Examples
    --------
    >>> jitter(np.ones(5), 1, seed=42)
    array([1.49671415, 0.8617357 , 1.64768854, 2.52302986, 0.76584663])
    """
    y = x if inplace else np.array(x, dtype=float, copy=True)

    generator = np.random.RandomState(seed)
    noise = generator.standard_normal(x.shape) * variance
    y += noise

    if clip is not None:
        lower, upper = clip
        np.clip(y, lower, upper, out=y)

    return y


@jit(nopython=True, nogil=True, cache=True)
def overlay_gaussian_blob(array, ux, uy, variance, intensity, roi=3):
    """Overlay image with a gaussian blob.

    Overlays a gaussian blob onto an image. The blob will only replace pixel
    values that are smaller than the calculated blob value.

    Parameters
    ----------
    array : ndarray
        Two-dimensional array representing an image which is modified in place.
    ux, uy : number
        Two positive numbers representing the center of the blob in cartesian
        coordinates. `uy` corresponds to the first and `ux` to the second
        `array` dimension.
    variance : number
        Square root of the variance of the gaussian blob in array coordinates.
    intensity : number
        Maximal value of the gaussian blob at its center.
    roi : number, optional
        Restricts the algorithm to a square region around the blob center.
        The squares size is calculated as 2 * sqrt(`variance`) * `roi`.
        This parameter is especially useful if the `variance` is small compared
        to the image size and can speed up the algorithm noticeably.
    """
    # # Alternative implementation: faster for large sigma
    # stop = (sigma * sigma_stop) ** 2
    # divisor = sigma ** 2 * 2
    # for ix in range(image.shape[0]):
    #     for iy in range(image.shape[1]):
    #         sqr_distance = (ix - ux) ** 2 + (iy - uy) ** 2
    #         if sqr_distance > stop:
    #             continue
    #         new_value = np.exp(-sqr_distance / divisor) * intensity
    #         if new_value > image[ix, iy]:
    #             image[ix, iy] = new_value

    # Calculate region of interest
    distance = np.sqrt(variance) * roi
    min_x = max(0, int(ux - distance))
    min_y = max(0, int(uy - distance))
    max_y = min(array.shape[0], int(uy + distance))
    max_x = min(array.shape[1], int(ux + distance))

    divisor = variance * 2
    for ix in range(min_x, max_x):
        for iy in range(min_y, max_y):
            sqr_distance = (ix - ux) ** 2 + (iy - uy) ** 2
            new_value = np.exp(-sqr_distance / divisor) * intensity

            if new_value > array[iy, ix]:
                array[iy, ix] = new_value


def white_noise(shape, *, mu=0, variance=1, seed=None):
    """Create frames with white noise.

    Parameters
    ----------
    shape : tuple[int]
        Dimension lengths of the generated frames.
    mu : float, optional
        The mean value of the generated white noise.
    variance : float, optional
        The variance of the generated white noise.
    seed : int, optional
        Used as a seed for the randomness generator. Using the same value for
        `seed` (and all other parameters) will result in the same output.

    Yields
    -------
    frame : np.ndarray
        The current frame.

    Notes
    -----
    Will generate frames infinitely and never raise a StopIteration.
    """
    generator = np.random.RandomState(seed)
    while True:
        frame = generator.standard_normal(shape)
        # TODO should this be variance or standard deviation
        frame *= variance
        frame += mu
        yield frame


def render_frames(particles, *, background):
    """Create frames from description.

    Parameters
    ----------
    particles : pandas.Dataframe[x, y, size, brightness, ...]
        DataFrame describing particle positions, as well as their size and
        brightness.
    background : ndarray or iterable[ndarray], optional
        A two-dimensional array or an iterable thereof used as the background
        for each generated frame.

    Yields
    ------
    frame : ndarray
        A frame with particles as described in `particles`.
    """
    if isinstance(background, np.ndarray):
        frame_count = particles["frame"].nunique()
        frames = (background.copy() for _ in range(frame_count))
    elif isinstance(background, Iterable):
        frames = background
    else:
        raise TypeError(
            "'background' must be None, an np.ndarray or an iterable of the former"
        )

    for frame, (_, frame_descr) in zip(frames, particles.groupby("frame")):
        for row in frame_descr.itertuples():
            overlay_gaussian_blob(
                array=frame,
                ux=row.x,
                uy=row.y,
                variance=row.size,
                intensity=row.brightness,
            )
        yield frame
