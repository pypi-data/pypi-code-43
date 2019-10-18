import os
import sys
import ntpath
import numpy as np
from itertools import groupby
import collections
from operator import itemgetter
from pynwb import NWBHDF5IO, NWBContainer
from pynwb.file import Subject
from PIL import ImageSequence
from ScanImageTiffReader import ScanImageTiffReader
import PIL.Image as pil_image
import time

def get_subfiles(current_path, relative_path=False, depth=1):
    # Get all files in the last directory of the path
    subfiles = []
    for (dirpath, dirnames, filenames) in os.walk(current_path):
        if relative_path:
            filenames = [os.path.join(dirpath, filename) for filename in filenames]
        subfiles.extend(filenames)
        depth -= 1
        if depth == 0:
            break
    return subfiles


def get_subdirs(current_path, depth=1):
    # Get all directories in the last directory of the path
    subdirs = []
    for (dirpath, dirnames, filenames) in os.walk(current_path):
        subdirs.extend(dirnames)
        depth -= 1
        if depth == 0:
            break
    return subdirs

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def get_continous_time_periods(binary_array):
    """
    take a binary array and return a list of tuples representing the first and last position(included) of continuous
    positive period
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
        # print(f"len(h[1][0]) {len(h[1][0])} h[1][0] {h[1][0]} h.size {h.size}")
        if np.any(h):
            result = []
            for i in np.arange(h.shape[1]):
                if h[1, i] == n_times-1:
                    result.append((h[0, i], h[1, i]))
                else:
                    result.append((h[0, i], h[1, i]-1))
            return result
    return []

def merging_time_periods(time_periods, min_time_between_periods):
    """
    Take a list of pair of values representing intervals (periods) and a merging thresholdd represented by
    min_time_between_periods. If the time between 2 periods are under this threshold, then we merge those periods.
    It returns a new list of periods.
    :param time_periods: list of list of 2 integers or floats. The second value represent the end of the period,
    the value being included in the period.
    :param min_time_between_periods: a float or integer value
    :return: a list of pair of list.
    """
    n_periods = len(time_periods)
    merged_time_periods = []
    index = 0
    while index < n_periods:
        time_period = time_periods[index]
        if len(merged_time_periods) == 0:
            merged_time_periods.append([time_period[0], time_period[1]])
            index += 1
            continue
        # we check if the time between both is superior at min_time_between_periods
        last_time_period = time_periods[index - 1]
        beg_time = last_time_period[1]
        end_time = time_period[0]
        if (end_time - beg_time) <= min_time_between_periods:
            # then we merge them
            merged_time_periods[-1][1] = time_period[1]
            index += 1
            continue
        else:
            merged_time_periods.append([time_period[0], time_period[1]])
        index += 1
    return merged_time_periods


def class_name_to_file_name(class_name):
    """
    Transform the string representing a class_name, by removing the upper case letters, and inserting
    before them an underscore if 2 upper case letters don't follow. Underscore are also inserted before numbers
    ex: ConvertAbfToNWB -> convert_abf_to_nwb
    :param class_name: string
    :return:
    """

    if len(class_name) == 1:
        return class_name.lower()

    new_class_name = class_name[0]
    for index in range(1, len(class_name)):
        letter = class_name[index]
        if letter.isdigit():
            # first we check if the previous letter was not a digit
            if class_name[index - 1].isupper():
                new_class_name = new_class_name + letter
                continue
            new_class_name = new_class_name + "_" + letter
            continue
        if not letter.isupper():
            new_class_name = new_class_name + letter
            continue
        # first we check if the previous letter was not upper
        if class_name[index - 1].isupper():
            new_class_name = new_class_name + letter
            continue
        new_class_name = new_class_name + "_" + letter

    return new_class_name.lower()


# def init_group_and_sort(nwb_path_list, param_list):
#
#     """
#
#     Args:
#         nwb_path_list (list): List of absolute path to NWB files
#         param_list (list): List of parameters to sort/group by
#
#     Returns:
#         result (list): values of param used to sort/group by
#
#     """
#
#     param_map = ["age", "sex", "genotype", "species", "subject_id", "weight", "date_of_birth",
#                  "session_start_time", "file_create_date", "experimenter", "session_id", "institution", "keywords",
#                  "pharmacology", "protocol", "related_pulication", "surgery", "virus", "lab"]
#
#     data_map = ["twophotonseries", "fluorescence", "roiresponseseries", "imagesegmentation", "planesegmentation",
#                 "device", "imagingplan", "opticalchannel", "raster"]
#
#     data_list = list()
#
#     def check_containers(container):
#         # recursive research of all containers (with 'children' field)
#         children = getattr(container, 'children', None)
#         for child in children:
#             if isinstance(child, NWBContainer) and not isinstance(child, Subject):
#                 data_list.append(str(type(child)).split("'")[1].split(".")[-1].lower())
#                 check_containers(child)
#
#     # Extract data from NWB and then sort it
#     result = []
#     for nwb_path in nwb_path_list:
#         nwb_result = []
#         io = NWBHDF5IO(nwb_path, 'r')
#         nwb_file = io.read()
#         check_containers(nwb_file)  # to get all containers
#
#         for param in param_list:
#             if param in param_map:
#                 param_in_metadata = getattr(nwb_file, param, None)
#                 param_in_subject_metadata = None
#                 if getattr(nwb_file, 'subject', None):
#                     param_in_subject_metadata = getattr(nwb_file.subject, param, None)
#
#                 if param_in_metadata:
#                     attrib = param_in_metadata
#                 elif param_in_subject_metadata:
#                     attrib = param_in_subject_metadata
#                 else:
#                     attrib = None
#
#             elif param.lower() in data_map:
#                 if param.lower() in data_list:
#                     attrib = True
#                 else:
#                     attrib = False
#
#             else:
#                 attrib = None
#
#             nwb_result.append(attrib)
#         nwb_result.append(nwb_file.identifier)
#         io.close()
#         result.append(nwb_result)
#
#     return result

#
# def group_by_param(nwb_path_list, param_list):
#
#     """
#     Group NWB files depending on a list of parameters
#
#     Args:
#         nwb_path_list (list): List of absolute path to NWB files
#         param_list (list): List of parameters to group by
#
#     Returns:
#         grouped_list (list): List of NWB files grouped
#         param_value_list (list) : List of values of the parameter that decided each group
#
#     """
#
#     result = init_group_and_sort(nwb_path_list, param_list)
#
#     grouped_list = []
#     param_value_list = []
#     sorted_list = sorted(result, key=lambda x: (x is None, x))
#     for k, g in groupby(sorted_list, itemgetter(0)):
#         t = list(zip(*g))
#         param_value_list.append(t[0][0])
#         grouped_list.append(list(t[len(t)-1]))
#     return grouped_list, param_value_list

class ComparableItem:
    """
    Make it possible to sort a list of items of different types, such as int and string
    """

    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        if isinstance(self.value, int) or isinstance(self.value, float):
            if isinstance(other.value, int) or isinstance(other.value, float):
                return self.value < other.value
            if isinstance(other.value, str):
                return True

        if isinstance(self.value, str):
            if isinstance(other.value, int) or isinstance(other.value, float):
                return False
            if isinstance(other.value, str):
                return self.value < other.value

        return True

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__()

def sort_by_param(nwb_path_list, param_list):

    """
    Sort NWB files depending on a list of parameters

    Args:
        nwb_path_list (list): List of absolute path to NWB files
        param_list (list): List of parameters to sort by

    Returns:
        nwb_sorted_list (list): List of NWB files sorted

    """

    result = init_group_and_sort(nwb_path_list, param_list)

    sorted_list = sorted(result, key=lambda x: (x is None, x))
    nwb_sorted_list = [nwb[len(sorted_list[0])-1] for nwb in sorted_list]
    return nwb_sorted_list


def flatten(list):
    """
    Flatten a nested list no matter the nesting level


    Args:
        list (list): List to flatten

    Returns:
        List without nest

    Examples:
        >>> flatten([1,2,[[3,4],5],[7]])
        [1,2,3,4,5,7]
    """

    if isinstance(list, collections.Iterable) and not isinstance(list, (str, bytes)):
        return [a for i in list for a in flatten(i)]
    else:
        return [list]


def load_tiff_movie_in_memory_using_pil(tif_movie_file_name, frames_to_add=None):
    """
        Load tiff movie from filename using PIL library

        Args:
            tif_movie_file_name (str) : Absolute path to tiff movie
            frames_to_add: dict with key an int representing the frame index after which add frames.
                the value is the number of frames to add (integer)

        Returns:
            tiff_movie (array) : Tiff movie as 3D-array
    """
    if frames_to_add is None:
        frames_to_add = dict()

    start_time_timer = time.time()
    im = pil_image.open(tif_movie_file_name)
    n_frames = len(list(ImageSequence.Iterator(im)))
    dim_y, dim_x = np.array(im).shape
    print(f"n_frames {n_frames}, dim_x {dim_x}, dim_y {dim_y}")

    if len(frames_to_add) > 0:
        n_frames += np.sum(list(frames_to_add.values()))
    tiff_movie = np.zeros((n_frames, dim_y, dim_x), dtype="uint16")
    frame_index = 0
    for frame, page in enumerate(ImageSequence.Iterator(im)):
        tiff_movie[frame_index] = np.array(page)
        frame_index += 1
        # adding blank frames
        if frame in frames_to_add:
            frame_index += frames_to_add[frame]
    stop_time_timer = time.time()
    print(f"Time for loading movie: "
          f"{np.round(stop_time_timer - start_time_timer, 3)} s")
    return tiff_movie


def load_tiff_movie_in_memory(tif_movie_file_name, frames_to_add=None):
    """
        Load tiff movie from filename using Scan Image Tiff

        Args:
            tif_movie_file_name (str) : Absolute path to tiff movie

        Returns:
            tiff_movie (array) : Tiff movie as 3D-array
    """

    if tif_movie_file_name is not None:
        print(f"Loading movie")
        try:
            if (frames_to_add is not None) and (len(frames_to_add) > 0):
                return load_tiff_movie_in_memory_using_pil(tif_movie_file_name, frames_to_add)
            else:
                raise AttributeError()
        except AttributeError:
            try:
                start_time = time.time()
                tiff_movie = ScanImageTiffReader(tif_movie_file_name).data()
                stop_time = time.time()
                print(f"Time for loading movie with scan_image_tiff: "
                      f"{np.round(stop_time - start_time, 3)} s")
            except Exception as e:
                return load_tiff_movie_in_memory_using_pil(tif_movie_file_name)

        return tiff_movie


def update_frames_to_add(frames_to_add, nwb_file, ci_sampling_rate):
    """
    Update frames_to_add (dict), based on pause_intervals and ci_frames_time_series
    Args:
        frames_to_add: dict, with key an int representing the frame index after which add frames.
        the value is the number of frames to add (integer)
        nwb_file: nwb file, will get nwb_file.intervals['ci_recording_on_pause'] and
        nwb_file.get_acquisition("ci_frames"), to update frames_to_add

    Returns:

    """
    try:
        pause_intervals = nwb_file.intervals['ci_recording_on_pause']
        pause_intervals_df = pause_intervals.to_dataframe()
        start_times = pause_intervals_df.loc[:, "start_time"]
        stop_times = pause_intervals_df.loc[:, "stop_time"]

        try:
            ci_frames_time_series = nwb_file.get_acquisition("ci_frames")
            ci_frames = np.where(ci_frames_time_series.data)[0]
            ci_frames_timestamps = ci_frames_time_series.timestamps[ci_frames]
            for i, start_time in enumerate(start_times):
                frame_index = np.searchsorted(a=ci_frames_timestamps, v=start_time)
                n_frames_to_add = (stop_times[i] - start_time) * ci_sampling_rate
                frames_to_add[frame_index] = int(n_frames_to_add)
        except KeyError:
            pass
    except KeyError:
        # if no 'ci_recording_on_pause' in nwb_file.intervals
        pass
