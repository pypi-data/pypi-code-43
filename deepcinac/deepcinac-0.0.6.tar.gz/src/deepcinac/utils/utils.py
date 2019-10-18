import numpy as np
from ScanImageTiffReader import ScanImageTiffReader
import time
import os
import PIL
from PIL import ImageSequence, ImageDraw
import tifffile
from shapely import geometry


def smooth_convolve(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    Source: https://scipy-cookbook.readthedocs.io/items/SignalSmooth.html

    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
    # print(len(s))
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')

    return y


def get_continous_time_periods(binary_array):
    """
    take a binary array and return a list of tuples representing the first and last position(included) of continuous
    positive period
    This code was copied from another project or from a forum, but i've lost the reference.
    :param binary_array:
    :return:
    """
    binary_array = np.copy(binary_array).astype("int8")
    n_times = len(binary_array)
    d_times = np.diff(binary_array)
    # show the +1 and -1 edges
    pos = np.where(d_times == 1)[0] + 1
    neg = np.where(d_times == -1)[0] + 1

    if (pos.size == 0) and (neg.size == 0):
        if len(np.nonzero(binary_array)[0]) > 0:
            return [(0, n_times-1)]
        else:
            return []
    elif pos.size == 0:
        # i.e., starts on an spike, then stops
        return [(0, neg[0])]
    elif neg.size == 0:
        # starts, then ends on a spike.
        return [(pos[0], n_times-1)]
    else:
        if pos[0] > neg[0]:
            # we start with a spike
            pos = np.insert(pos, 0, 0)
        if neg[-1] < pos[-1]:
            #  we end with aspike
            neg = np.append(neg, n_times - 1)
        # NOTE: by this time, length(pos)==length(neg), necessarily
        h = np.matrix([pos, neg])
        if np.any(h):
            result = []
            for i in np.arange(h.shape[1]):
                if h[1, i] == n_times-1:
                    result.append((h[0, i], h[1, i]))
                else:
                    result.append((h[0, i], h[1, i]-1))
            return result
    return []

def create_one_tiff_file_by_frame(movies_to_split, results_path, verbose=0):
    """
    Split a calcium imaging movie so that each frame will be saved as a tiff image.
    If the directory for results already contains a directory of the name of the movie identifier,
    the data won't be erased.
    Args:
        movies_to_split: a dictionary with as a key an identifier for the movie that will be used to name
        the directory in which the tiff will be put (using lower case), and as value either the file_name
        of the tiff or an numpy float
        ndarray representing the calcium imaging data (should n_frames * n_pixels_x * n_pixels_y)
        results_path: String. The directory in which will be created the directories containing the tiff files.
        verbose: Integer. 0, 1, or 2. Verbosity mode. 0 = silent, 1 = times for main operation, 2 = various prints.

    Returns: None

    """

    if verbose == 2:
        print("create_one_tiff_file_by_frame")

    # first we get a list of all movies already splited as tiff files
    dir_names = []
    # look for filenames in the fisst directory, if we don't break, it will go through all directories
    for (dirpath, dirnames, local_filenames) in os.walk(results_path):
        dir_names.extend([x.lower() for x in dirnames])
        break

    for identifier, movie_value in movies_to_split.items():
        if identifier.lower() in dirnames:
            if verbose == 2:
                print(f"Tiffs for {identifier} already existing")
            # it means we've already created the tiffs
            continue

        if verbose == 2:
            print(f"Creating tiffs for {identifier}")
        if isinstance(movie_value, str):
            try:
                start_time = time.time()
                tiff_movie = ScanImageTiffReader(movie_value).data()
                n_frames = len(tiff_movie)
                stop_time = time.time()
                if verbose >= 1:
                    print(f"Time for loading movie with scan_image_tiff: "
                          f"{np.round(stop_time - start_time, 3)} s")
            except Exception as e:
                start_time = time.time()
                im = PIL.Image.open(movie_value)
                n_frames = len(list(ImageSequence.Iterator(im)))
                dim_y, dim_x = np.array(im).shape
                if verbose == 2:
                    print(f"n_frames {n_frames}, dim_x {dim_x}, dim_y {dim_y}")
                tiff_movie = np.zeros((n_frames, dim_y, dim_x), dtype="uint16")
                for frame, page in enumerate(ImageSequence.Iterator(im)):
                    tiff_movie[frame] = np.array(page)
                stop_time = time.time()
                if verbose >= 1:
                    print(f"Time for loading movie: "
                          f"{np.round(stop_time - start_time, 3)} s")
        else:
            tiff_movie = movie_value

        ms_path = os.path.join(results_path, identifier.lower())
        os.mkdir(ms_path)

        # saving the mean and std value of the movie, for later on normalization.
        mean_value = np.mean(tiff_movie)
        std_value = np.std(tiff_movie)
        np.save(os.path.join(ms_path, "mean.npy"), mean_value)
        np.save(os.path.join(ms_path, "std.npy"), std_value)

        start_time = time.time()
        # then saving each frame as a unique tiff
        for frame in np.arange(n_frames):
            tiff_file_name = os.path.join(ms_path, f"{frame}.tiff")
            with tifffile.TiffWriter(tiff_file_name) as tiff:
                tiff.save(tiff_movie[frame], compress=0)
        stop_time = time.time()
        if verbose >= 1:
            print(f"Time for writing the tiffs: "
                  f"{np.round(stop_time - start_time, 3)} s")

        # to free memory
        if isinstance(movie_value, str):
            del tiff_movie


def scale_polygon_to_source(polygon, minx, miny):
    """
    Take an instance of shapely.geometry.Polygon or shapely.geometry.LineString and scale it, so that each of
     it coordinates are substracted by minx and miny on the x and y axis respectively
    coordinates to match minx and miny
    Args:
        polygon: Polygon instance from shapely package. Could also be a LineString
        minx: integer
        miny: integer

    Returns: a new shapely.geometry.Polygon or shapely.geometry.LineString

    """
    if isinstance(polygon, geometry.LineString):
        coords = list(polygon.coords)
    else:
        coords = list(polygon.exterior.coords)

    scaled_coords = []
    for coord in coords:
        scaled_coords.append((coord[0] - minx, coord[1] - miny))

    if isinstance(polygon, geometry.LineString):
        return geometry.LineString(scaled_coords)
    else:
        return geometry.Polygon(scaled_coords)


def load_movie(file_name, with_normalization, verbose=True):
    """
    Load a movie in memory. So far only tiff format is valid
    Args:
        file_name:
        with_normalization: if True, normalize the movie using z-score formula

    Returns:

    """
    try:
        start_time = time.time()
        tiff_movie = ScanImageTiffReader(file_name).data()
        stop_time = time.time()
        if verbose:
            print(f"Time for loading movie with ScanImageTiffReader: "
                  f"{np.round(stop_time - start_time, 3)} s")
    except Exception as e:
        start_time = time.time()
        im = PIL.Image.open(file_name)
        n_frames = len(list(ImageSequence.Iterator(im)))
        dim_y, dim_x = np.array(im).shape
        tiff_movie = np.zeros((n_frames, dim_y, dim_x), dtype="uint16")
        for frame, page in enumerate(ImageSequence.Iterator(im)):
            tiff_movie[frame] = np.array(page)
        stop_time = time.time()
        if verbose:
            print(f"Time for loading movie with PIL: "
                  f"{np.round(stop_time - start_time, 3)} s")
    if with_normalization:
        tiff_movie_normalized = tiff_movie - np.mean(tiff_movie)
        tiff_movie_normalized = tiff_movie_normalized / np.std(tiff_movie)
        return tiff_movie_normalized
    else:
        return tiff_movie


def get_source_profile_param(cell, movie_dimensions, coord_obj, max_width, max_height, pixels_around=0,
                             buffer=None, with_all_masks=False, get_only_polygon_contour=False):
    """
     For given cell, get the binary mask representing this cell with the possibility to get the binary masks
     of the cells it intersects with.

    Args:
        cell:
        movie_dimensions: tuple of integers, width and height of the movie
        coord_obj: instance of
        max_width:
        max_height:
        pixels_around: how many pixels to add around the frame containing the cell, doesn't change the mask
        buffer: How much pixels to scale the cell contour in the mask. If buffer is 0 or None, then size of the cell
        won't change.
        with_all_masks: Return a dict with all overlaps cells masks + the main cell mask. The key is an int.
     The mask consist on a binary array of with 0 for all pixels in the cell, 1 otherwise
        get_only_polygon_contour: the mask represents then only the pixels that makes the contour of the cells

    Returns: A mask (numpy 2d binary array), with 0 for all pixels in the cell, 1 otherwise.
     A tuple with four integers representing the corner coordinates (minx, maxx, miny, maxy)

    """
    len_frame_x = movie_dimensions[1]
    len_frame_y = movie_dimensions[0]

    # determining the size of the square surrounding the cell so it includes all overlapping cells around
    overlapping_cells = coord_obj.intersect_cells[cell]
    cells_to_display = [cell]
    cells_to_display.extend(overlapping_cells)

    # calculating the bound that will surround all the cells
    minx = None
    maxx = None
    miny = None
    maxy = None

    for cell_to_display in cells_to_display:
        poly_gon = coord_obj.cells_polygon[cell_to_display]

        if minx is None:
            minx, miny, maxx, maxy = np.array(list(poly_gon.bounds)).astype(int)
        else:
            tmp_minx, tmp_miny, tmp_maxx, tmp_maxy = np.array(list(poly_gon.bounds)).astype(int)
            minx = min(minx, tmp_minx)
            miny = min(miny, tmp_miny)
            maxx = max(maxx, tmp_maxx)
            maxy = max(maxy, tmp_maxy)

    minx = max(0, minx - pixels_around)
    miny = max(0, miny - pixels_around)
    # we use max_width and max_height to make sure it won't be bigger than the frame used by the network
    # and we crop the frame if necessary
    maxx = np.min(((len_frame_x - 1), (maxx + pixels_around), (minx + max_height - 1)))
    maxy = np.min(((len_frame_y - 1), (maxy + pixels_around), (miny + max_width - 1)))

    len_x = maxx - minx + 1
    len_y = maxy - miny + 1

    mask_dict = dict()

    for cell_to_display in cells_to_display:
        if (not with_all_masks) and (cell_to_display != cell):
            continue
        polygon = coord_obj.cells_polygon[cell_to_display]
        # mask used in order to keep only the cells pixel
        # the mask put all pixels in the polygon, including the pixels on the exterior line to zero
        scaled_polygon = scale_polygon_to_source(polygon=polygon, minx=minx, miny=miny)
        img = PIL.Image.new('1', (len_x, len_y), 1)
        if buffer is not None:
            scaled_polygon = scaled_polygon.buffer(buffer)
        fill_value = 0
        if get_only_polygon_contour:
            fill_value = None
        if isinstance(scaled_polygon, geometry.LineString):
            ImageDraw.Draw(img).polygon(list(scaled_polygon.coords), outline=0,
                                        fill=fill_value)
        else:
            ImageDraw.Draw(img).polygon(list(scaled_polygon.exterior.coords), outline=0,
                                        fill=fill_value)

        mask_dict[cell_to_display] = np.array(img)

    if with_all_masks:
        return mask_dict, (minx, maxx, miny, maxy)
    else:
        return mask_dict[cell], (minx, maxx, miny, maxy)


def welsh_powell(graph):
    """
	implementation of welsh_powell algorithm
	https://github.com/MUSoC/Visualization-of-popular-algorithms-in-Python/blob/master/Graph%20Coloring/graph_coloring.py
	Args:
		graph: instance of networkx graph

	Returns:

    """
    # sorting the nodes based on it's valency
    node_list = sorted(graph.nodes(), key=lambda x: graph.degree(x))
    # dictionary to store the colors assigned to each node
    col_val = {}
    # assign the first color to the first node
    col_val[node_list[0]] = 0
    # Assign colors to remaining N-1 nodes
    for node in node_list[1:]:
        available = [True] * len(graph.nodes())  # boolean list[i] contains false if the node color 'i' is not available

        # iterates through all the adjacent nodes and marks it's color as unavailable, if it's color has been set already
        for adj_node in graph.neighbors(node):
            if adj_node in col_val.keys():
                col = col_val[adj_node]
                available[col] = False
        clr = 0
        for clr in range(len(available)):
            if available[clr] == True:
                break
        col_val[node] = clr

    return col_val

############################################################################################
############################################################################################
############################### data augmentation functions ###############################
############################################################################################
############################################################################################

def horizontal_flip(movie):
    """
    movie is a 3D numpy array
    :param movie:
    :return:
    """
    new_movie = np.zeros(movie.shape)
    for frame in np.arange(len(movie)):
        new_movie[frame] = np.fliplr(movie[frame])

    return new_movie


def vertical_flip(movie):
    """
    movie is a 3D numpy array
    :param movie:
    :return:
    """
    new_movie = np.zeros(movie.shape)
    for frame in np.arange(len(movie)):
        new_movie[frame] = np.flipud(movie[frame])

    return new_movie


def v_h_flip(movie):
    """
    movie is a 3D numpy array
    :param movie:
    :return:
    """
    new_movie = np.zeros(movie.shape)
    for frame in np.arange(len(movie)):
        new_movie[frame] = np.fliplr(np.flipud(movie[frame]))

    return new_movie


def rotate_movie(movie, angle):
    """
        movie is a 3D numpy array
        :param movie:
        :return:
        """
    new_movie = np.zeros(movie.shape)
    for frame in np.arange(len(movie)):
        new_movie[frame] = ndimage.rotate(movie[frame], angle=angle, reshape=False, mode='reflect')

    return new_movie


def shift_movie(movie, x_shift, y_shift):
    """
    movie is a 3D numpy array
    :param movie:
    :param x_shift:
    :param y_shift:
    :return:
    """
    if x_shift >= movie.shape[2]:
        raise Exception(f"x_shift {x_shift} >= movie.shape[2] {movie.shape[2]}")
    if y_shift >= movie.shape[1]:
        raise Exception(f"y_shift {y_shift} >= movie.shape[1] {movie.shape[1]}")

    new_movie = np.zeros(movie.shape)

    if (y_shift == 0) and (x_shift == 0):
        new_movie = movie[:, :, :]
    elif (y_shift == 0) and (x_shift > 0):
        for frame in np.arange(len(movie)):
            new_movie[frame, :, :-x_shift] = movie[frame, :, x_shift:]
    elif (y_shift == 0) and (x_shift < 0):
        for frame in np.arange(len(movie)):
            new_movie[frame, :, -x_shift:] = movie[frame, :, :x_shift]
    elif (y_shift > 0) and (x_shift == 0):
        for frame in np.arange(len(movie)):
            new_movie[frame, :-y_shift, :] = movie[frame, y_shift:, :]
    elif (y_shift < 0) and (x_shift == 0):
        for frame in np.arange(len(movie)):
            new_movie[frame, -y_shift:, :] = movie[frame, :y_shift, :]
    elif (y_shift > 0) and (x_shift > 0):
        for frame in np.arange(len(movie)):
            new_movie[frame, :-y_shift, :-x_shift] = movie[frame, y_shift:, x_shift:]
    elif (y_shift < 0) and (x_shift < 0):
        for frame in np.arange(len(movie)):
            new_movie[frame, -y_shift:, -x_shift:] = movie[frame, :y_shift, :x_shift]
    elif (y_shift > 0) and (x_shift < 0):
        for frame in np.arange(len(movie)):
            new_movie[frame, :-y_shift, -x_shift:] = movie[frame, y_shift:, :x_shift]
    elif (y_shift < 0) and (x_shift > 0):
        for frame in np.arange(len(movie)):
            new_movie[frame, -y_shift:, :-x_shift] = movie[frame, :y_shift, x_shift:]

    return new_movie
