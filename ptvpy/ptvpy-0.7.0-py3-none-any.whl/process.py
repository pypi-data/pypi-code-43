"""Tools for particle tracking velocimetry."""


import numpy as np
import pandas as pd
from numba import jit
from scipy import interpolate, spatial

from .utils import expected_warning


__all__ = [
    "xy_velocity",
    "absolute_velocity",
    "scatter_to_regular",
    "find_helix_particles",
    "mean_frame",
]


def xy_velocity(data, step=1):
    """Calculate displacement for each particle between consecutive frames.

    Parameters
    ----------
    data : pandas.DataFrame[frame, particle, x, y]
        Trajectories of particles. Column "frame" is treated as the time axis.
    step : int, optional
        Only calculate displacement between frames this many steps apart. The
        resulting values are normalized with `step`. Thus dx and dy always
        give a pixel displacement per frame.

    Returns
    -------
    out : pandas.DataFrame[frame, particle, x, y, dx, dy]
        Velocity for each row in `data` in each direction.
    """
    if not isinstance(step, int):
        raise TypeError("step must be an int, was {}".format(type(step)))
    if step < 1:
        raise ValueError("step must be at least 1, was {}".format(step))

    out = data.copy()
    if len(out.index) == 0:
        diff = pd.DataFrame(np.zeros((0, 2)))
    else:
        out.sort_values(["particle", "frame"], inplace=True)
        diff = out.groupby("particle")["x", "y"].diff(step) / step
    out[["dx", "dy"]] = diff
    return out


def absolute_velocity(data):
    """Calculate absolute velocity for each frame and particle.

    Parameters
    ----------
    data : pandas.DataFrame[dx, dy]
        Velocities in x and y direction.

    Returns
    -------
    out : pandas.DataFrame[dx, dy, v]
        Absolute velocity for each row in `data`.
    """
    out = data.copy()
    out["v"] = np.sqrt(data["dx"] ** 2 + data["dy"] ** 2)
    return out


def _in_convex_hull(test_points, hull_points):
    """Test if points are inside a convex hull.

    Parameters
    ----------
    test_points : numpy.ndarray, shape (M, D)
        Coordinates of the points to test.
    hull_points : numpy.ndarray, shape (N, D)
        Coordinates of the point cloud that forms the convex hull.

    Returns
    -------
    inside : numpy.ndarray[bool], shape (M,)
        True where a point in `test_points` is inside the convex hull otherwise
        false.
    """
    # https://stackoverflow.com/a/16898636
    hull = spatial.Delaunay(hull_points)
    return hull.find_simplex(test_points) != -1


def _digitize(x, bin_count):
    """Round values to a new discrete linear space of given length.

    Parameters
    ----------
    x : numpy.ndarray
        Array to digitize.
    bin_count : int
        Length of the new space.

    Returns
    -------
    d : numpy.ndarray
        An array with the same shape, minimal and maximal value as `x` but
        whose values were rounded to the linear space..
    space : numpy.ndarray
        The new linear space.
    """
    x_min, x_max = x.min(), x.max()
    half_step = (x_max - x_min) / bin_count / 2
    # Create new linear space
    centers = np.linspace(x_min, x_max, bin_count)
    # Create bins around each value in linear space
    bins = np.linspace(x_min - half_step, x_max + half_step, bin_count + 1)
    # Correct returned indices by -1
    return centers[np.digitize(x, bins) - 1], centers


def scatter_to_regular(
    vectors,
    data=None,
    extrapolate=False,
    fit_shape=None,
    grid_shape=None,
    smooth=4,
    as_df=True,  # TODO remove or add documentation
):
    """Interpolate scattered data onto a regular grid.

    This is a wrapper around `scipy.spatial.Rbf` that can down-sample the input
    space for faster interpolation-fitting. Optionally extrapolation outside
    the convex hull of the input space can be turned off.

    Parameters
    ----------
    vectors : tuple[str]
        Names matching columns in `data`. All values in `vectors` are treated
        as coordinates except for the last which is treated as the scalar
        field's values.
    data : pandas.DataFrame, optional, columns same as vectors
        Optional DataFrame with columns matching the 4 variables above.
    extrapolate : bool, optional
        If False, only return values that lie in the convex hull of the
        scattered scalar field.
    fit_shape : tuple[int], optional
        Resolution in each dimension used for interpolation.
    grid_shape : tuple[int], optional
        Resolution in each dimension for the returned regular scalar field.
    smooth : float, optional
        An optional factor used to smooth the interpolated output. Bigger
        values increase smoothness.

    Returns
    -------
    out : pandas.DataFrame, columns same as vectors
        The first columns in `out` form a regular sized grid while the last
        contains interpolated values for new positions.

    References
    ----------
    https://stackoverflow.com/a/37872172
    """
    data = data[list(vectors)]
    data = data.dropna(axis=0, how="any")

    c_names = list(data.columns[:-1])
    v_name = data.columns[-1]

    default_dim_size = int(1e3 ** (1 / len(c_names)))
    if fit_shape is None:
        fit_shape = np.full(len(c_names), default_dim_size)
    if grid_shape is None:
        grid_shape = np.full(len(c_names), default_dim_size)

    if fit_shape is False:
        resampled = data
    else:
        for i, c in enumerate(c_names):
            data[c], _ = _digitize(data[c], fit_shape[i])

        grouped = data.groupby(c_names)
        resampled = grouped[v_name].median().to_frame()
        resampled["weights"] = grouped.sum()
        resampled.reset_index(drop=False, inplace=True)

    rbf = interpolate.Rbf(
        *[resampled[name] for name in c_names], resampled[v_name], smooth=smooth
    )

    c_spaces = [
        np.linspace(data[name].min(), data[name].max(), length)
        for name, length in zip(c_names, grid_shape)
    ]
    c_grids = np.meshgrid(*c_spaces)
    v_grid = rbf(*c_grids)

    if not extrapolate:
        hull_points = resampled[c_names].values
        grid_points = np.vstack([grid.ravel() for grid in c_grids]).T
        not_in_hull = ~_in_convex_hull(grid_points, hull_points)
        v_grid.ravel()[not_in_hull] = np.nan

    if as_df:
        out = {name: grid.ravel() for name, grid in zip(c_names, c_grids)}
        out[v_name] = v_grid.ravel()
        out = pd.DataFrame(out)
    else:
        out = (*c_grids, v_grid)

    return out


@jit(nopython=True, nogil=True, cache=True)
def _find_point_pairs(points, min_distance, max_distance, unique):
    """Find point pairs in n-dimensional coordinate system.

    This function finds point pairs out of all possible ones based on their
    euclidean distance to each other.

    Parameters
    ----------
    points : ndarray, dtype np.float64
        2D array with the shape (m, n) where m is the number of points and
        n is the number of each point's coordinates (e.g. n = 2 for a plane).
    min_distance : scalar
        Minimal euclidean distance for two points to be considered a pair.
    max_distance : scalar
        Maximal euclidean distance for two points to be considered a pair.
    unique : bool
        Ensure that each point appears only in one pair. If a point has more
        than one neighbor within the allowed distance the closest one is
        chosen. If both neighbors are equally close the first one is picked.

    Returns
    -------
    pairs : ndarray, shape (N, 2)
        Array with pairs of indices to `points`.
    distances : ndarray, (N,)
        Array with euclidean distance (not squared!) between each pair in
        `pairs`.

    Examples
    --------
    >>> points = np.array([(1, 1), (1, 2), (2, 1), (2, 2)], dtype=np.float64)
    >>> _find_point_pairs(points, 0, 2, unique=False)
    (array([[0, 1],
           [0, 2],
           [0, 3],
           [1, 2],
           [1, 3],
           [2, 3]]), array([1.        , 1.        , 1.41421356, 1.41421356, 1.        ,
           1.        ]))
    >>> _find_point_pairs(points, 0, 1.5, unique=True)
    (array([[0, 1],
           [2, 3]]), array([1., 1.]))
    >>> _find_point_pairs(points, 1.1, 1.5, unique=True)
    (array([[0, 3],
           [1, 2]]), array([1.41421356, 1.41421356]))
    """
    # Find rows that match distance condition
    pairs = []
    distances = []
    # Iterate combination (i, j) of all rows
    for i in range(points.shape[0]):
        for j in range(i + 1, points.shape[0]):
            # Calculate euclidean distance (2-norm)
            distance = np.linalg.norm(points[i, :] - points[j, :])
            if min_distance <= distance <= max_distance:
                # and append if distance condition matches
                pairs.append((i, j))
                distances.append(distance)

    pairs = np.array(pairs) if pairs else np.empty((0, 2), dtype=np.intp)
    distances = np.array(distances)

    if unique:
        # Sort pairs by distance, which ensures that the maximal number of
        # unique pairs is found. E.g. we have pair distances A > B > C.
        # Comparing in this order will flag A for deletion and then B, leaving
        # C. Comparing in reverse order will compare B & C first, discard B and
        # leave A and C as pairs.
        sort_index = np.argsort(distances)
        pairs = pairs[sort_index]
        distances = distances[sort_index]

        # Prepare array of flags for each pair (initially True)
        flags = np.ones(pairs.shape[0], dtype=np.bool_)
        # Iterate combination (i, j) of all pairs
        for i in range(pairs.shape[0]):
            for j in range(i + 1, pairs.shape[0]):
                # Check if both pairs are still candidates
                if (
                    flags[i]
                    and flags[j]
                    and (
                        # and share indices
                        pairs[i, 0] == pairs[j, 0]
                        or pairs[i, 0] == pairs[j, 1]
                        or pairs[i, 1] == pairs[j, 0]
                        or pairs[i, 1] == pairs[j, 1]
                    )
                ):
                    # Flag one pair for deletion, flagging the second element
                    # even if both distances are equal ensures that pairs are
                    # truly unique
                    if distances[i] <= distances[j]:
                        flags[j] = False
                    else:
                        flags[i] = False

        # Only keep pairs that are still flagged
        pairs = pairs[flags, :]
        distances = distances[flags]

    return pairs, distances


def find_helix_particles(
    particles, min_distance, max_distance, unique=True, save_old_pos=False
):
    """Match particles in a single frame into pairs.

    Parameters
    ----------
    particles : pandas.DataFrame[x, y, ...]
        A DataFrame containing the detected particle positions of a single
        frame.
    min_distance : scalar
        Minimal euclidean distance for two particles to be considered a pair.
    max_distance : scalar
        Maximal euclidean distance for two particles to be considered a pair.
    unique : bool, optional
        Ensure that each particle appears only in one pair. If a particle has
        more than one neighbor within the allowed distance the closest one is
        chosen. If both neighbors are equally close the first one is picked.
    save_old_pos : bool, optional
        If True, the old positions of the two particles forming a pair are
        stored inside the columns "x_old_i" and "y_old_i" with i in [1, 2].

    Returns
    -------
    helix_particles : pandas.DataFrame[x, y, pair_distance, angle, ...]
        New DataFrame with the particle pairs in the current frame.

    Notes
    -----
    The algorithm used to find pairs can be summarized as follows:

    1. Calculate the euclidean distance for all possible particle combinations
       and select candidates based on the constrains `min_distance` and
       `max_distance`.
    2. If `unique` is required, sort all candidates by their distance
       (ascending). Iterate all possible candidate combinations, if two
       candidates share the same particle, remove the one with the larger
       distance. If their distance is equal, remove the second one.
    3. Return remaining candidates and their distances.

    Because of the algorithm's fast growing complexity O(n^4), reducing the
    number of candidates in step 1 by allowing only a narrow distance range
    is performance critical.
    """
    coords = particles.loc[:, ["x", "y"]].values
    pairs, distances = _find_point_pairs(
        coords.astype(np.float64),
        np.float64(min_distance),
        np.float64(max_distance),
        bool(unique),
    )

    # Construct new DataFrame with averaged statistics
    # This part takes the bulk of the processing time; is there a way to
    # do this faster?
    left_frame = particles.iloc[pairs[:, 0]].reset_index(drop=True)
    right_frame = particles.iloc[pairs[:, 1]].reset_index(drop=True)
    helix_particles = pd.concat([left_frame, right_frame])
    helix_particles = helix_particles.groupby(helix_particles.index).mean()

    # And add new data
    x = coords[pairs, 0]
    y = coords[pairs, 1]
    if save_old_pos:
        helix_particles["x_old_1"] = x[:, 0]
        helix_particles["x_old_2"] = x[:, 1]
        helix_particles["y_old_1"] = y[:, 0]
        helix_particles["y_old_2"] = y[:, 1]
    x_diff = np.diff(x).ravel()
    y_diff = np.diff(y).ravel()
    with expected_warning("divide by zero", RuntimeWarning):
        helix_particles["angle"] = np.arctan(y_diff / x_diff)
    helix_particles["pair_distance"] = distances

    return helix_particles


def mean_frame(frames):
    """Calculate the average per pixel for all frames.

    This function essentially does the same as ``np.mean(frames, axis=-1)`` but
    doesn't need to hold all items in `frames` in memory at once. Instead the
    average is calculated incrementally.

    Parameters
    ----------
    frames : Iterable[ndarray]
        Iterable of arrays with the same shape.

    Returns
    -------
    background : ndarray
        An array with the same shape as each element in `frames` containing
        the average per pixel.
    """
    background = np.zeros(frames[0].shape, dtype=np.float64)
    length = len(frames)
    for frame in frames:
        background += frame / length
    return background
