# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

from __future__ import print_function

import base64
import calendar
import functools
import getpass
import io
import json
import logging
import math
import operator
import os
import os.path
import tempfile
import time
from datetime import datetime

import six
from pkg_resources import DistributionNotFound, get_distribution

LOGGER = logging.getLogger(__name__)


if six.PY2:
    from StringIO import StringIO
else:
    StringIO = io.StringIO


if hasattr(time, "monotonic"):
    get_time_monotonic = time.monotonic
else:
    # Python2 just won't have accurate time durations
    # during clock adjustments, like leap year, etc.
    get_time_monotonic = time.time


def is_iterable(value):
    try:
        iter(value)
        return True

    except TypeError:
        return False


def is_list_like(value):
    """ Check if the value is a list-like
    """
    if is_iterable(value) and not isinstance(value, six.string_types):
        return True

    else:
        return False


def to_utf8(str_or_bytes):
    if hasattr(str_or_bytes, "decode"):
        return str_or_bytes.decode("utf-8", errors="replace")

    return str_or_bytes


def local_timestamp():
    """ Return a timestamp in a format expected by the backend (milliseconds)
    """
    now = datetime.utcnow()
    timestamp_in_seconds = calendar.timegm(now.timetuple()) + (now.microsecond / 1e6)
    timestamp_in_milliseconds = int(timestamp_in_seconds * 1000)
    return timestamp_in_milliseconds


def wait_for_empty(check_function, timeout, verbose=False, sleep_time=1):
    """ Wait up to TIMEOUT seconds for the messages queue to be empty
    """
    end_time = time.time() + timeout
    while check_function() is False and time.time() < end_time:
        if verbose is True:
            LOGGER.info("Still uploading")
        # Wait a max of sleep_time, but keep checking to see if
        # check_function is done. Allows wait_for_empty to end
        # before sleep_time has elapsed:
        end_sleep_time = time.time() + sleep_time
        while check_function() is False and time.time() < end_sleep_time:
            time.sleep(sleep_time / 20)


def read_unix_packages():
    # () -> Optional[List[str]]
    package_status_file = "/var/lib/dpkg/status"
    if os.path.isfile(package_status_file):
        with open(package_status_file, "r") as f:
            status = f.read()
        package = None
        os_packages = []
        for line in status.split("\n"):
            if line.startswith("Package: "):
                package = line[9:]
            if line.startswith("Version: "):
                version = line[9:]
                if package is not None:
                    os_packages.append((package, version))
                package = None
        os_packages_list = sorted(
            [("%s=%s" % (package, version)) for (package, version) in os_packages]
        )
        return os_packages_list
    else:
        return None


def image_data_to_file_like_object(
    image_data,
    file_name,
    image_format,
    image_scale,
    image_shape,
    image_colormap,
    image_minmax,
    image_channels,
):
    """
    Ensure that the given image_data is converted to a file_like_object ready
    to be uploaded
    """
    try:
        import PIL.Image
    except ImportError:
        PIL = None

    ## Conversion from standard objects to image
    ## Allow file-like objects, numpy arrays, etc.
    if hasattr(image_data, "numpy"):  # pytorch tensor
        array = image_data.numpy()
        fp = array_to_image_fp(
            array,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )

        return fp
    elif hasattr(image_data, "eval"):  # tensorflow tensor
        array = image_data.eval()
        fp = array_to_image_fp(
            array,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )

        return fp
    elif PIL is not None and isinstance(image_data, PIL.Image.Image):  # PIL.Image
        ## filename tells us what format to use:
        if file_name is not None and "." in file_name:
            _, image_format = file_name.rsplit(".", 1)
        fp = image_to_fp(image_data, image_format)

        return fp
    elif image_data.__class__.__name__ == "ndarray":  # numpy array
        fp = array_to_image_fp(
            image_data,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )

        return fp
    elif hasattr(image_data, "read"):  # file-like object
        return image_data
    elif isinstance(image_data, (tuple, list)):  # list or tuples
        try:
            import numpy
        except ImportError:
            LOGGER.error("The Python library numpy is required for this operation")
            return None
        array = numpy.array(image_data)
        fp = array_to_image_fp(
            array,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )
        return fp
    else:
        LOGGER.error("invalid image file_type: %s", type(image_data))
        if PIL is None:
            LOGGER.error("Consider installing the Python Image Library, PIL")
        return None


def array_to_image_fp(
    array,
    image_format,
    image_scale,
    image_shape,
    image_colormap,
    image_minmax,
    image_channels,
):
    """
    Convert a numpy array to an in-memory image
    file pointer.
    """
    try:
        import PIL.Image
        import numpy as np
        from matplotlib import cm
    except ImportError:
        LOGGER.error(
            "The Python libraries PIL, numpy, and matplotlib are required for this operation"
        )
        return

    ## Handle image transformations here
    ## End up with a 0-255 PIL Image
    if image_minmax is not None:
        minmax = image_minmax
    else:  # auto minmax
        minmax = [array.min(), array.max()]
        if minmax[0] == minmax[1]:
            minmax[0] = minmax[0] - 0.5
            minmax[1] = minmax[1] + 0.5
        minmax[0] = math.floor(minmax[0])
        minmax[1] = math.ceil(minmax[1])
    ## if a shape is given, try to reshape it:
    if image_shape is not None:
        try:
            ## array shape is opposite of image size(width, height)
            array = array.reshape(image_shape[1], image_shape[0])
        except Exception:
            LOGGER.info("WARNING: invalid image_shape; ignored", exc_info=True)
    ## If 3D, but last array is flat, make it 2D:
    if len(array.shape) == 3 and array.shape[-1] == 1:
        array = array.reshape((array.shape[0], array.shape[1]))
    elif len(array.shape) == 1:
        ## if 1D, make it 2D:
        array = np.array([array])
    if image_channels == "first" and len(array.shape) == 3:
        array = np.moveaxis(array, 0, -1)
    ### Ok, now let's colorize and scale
    if image_colormap is not None:
        ## Need to be in range (0,1) for colormapping:
        array = rescale_array(array, minmax, (0, 1), "float")
        try:
            cm_hot = cm.get_cmap(image_colormap)
            array = cm_hot(array)
        except Exception:
            LOGGER.info("WARNING: invalid image_colormap; ignored", exc_info=True)
        ## rescale again:
        array = rescale_array(array, (0, 1), (0, 255), "uint8")
        ## Convert to RGBA:
        image = PIL.Image.fromarray(array, "RGBA")
    else:
        ## Rescale (0, 255)
        array = rescale_array(array, minmax, (0, 255), "uint8")
        image = PIL.Image.fromarray(array)
    if image_scale != 1.0:
        image = image.resize(
            (int(image.size[0] * image_scale), int(image.size[1] * image_scale))
        )
    ## Put in a standard mode:
    if image.mode not in ["RGB", "RGBA"]:
        image = image.convert("RGB")
    return image_to_fp(image, image_format)


def image_to_fp(image, image_format):
    """
    Convert a PIL.Image into an in-memory file
    pointer.
    """
    fp = io.BytesIO()
    image.save(fp, format=image_format)  # save the content to fp
    fp.seek(0)
    return fp


def rescale_array(array, old_range, new_range, dtype):
    """
    Given a numpy array in an old_range, rescale it
    into new_range, and make it an array of dtype.
    """
    try:
        import numpy as np
    except ImportError:
        LOGGER.error("The Python library numpy is required for this operation")
        return

    old_min, old_max = old_range
    if array.min() < old_min or array.max() > old_max:
        ## truncate:
        array = np.clip(array, old_min, old_max)
    new_min, new_max = new_range
    old_delta = float(old_max - old_min)
    new_delta = float(new_max - new_min)
    if old_delta == 0:
        return ((array - old_min) + (new_min + new_max) / 2).astype(dtype)
    else:
        return (new_min + (array - old_min) * new_delta / old_delta).astype(dtype)


def write_file_like_to_tmp_file(file_like_object):
    # Copy of `shutil.copyfileobj` with binary / text detection

    buf = file_like_object.read(1)

    # Detect binary/text
    if isinstance(buf, six.binary_type):
        tmp_file_mode = "w+b"
    else:
        tmp_file_mode = "w+"

    tmp_file = tempfile.NamedTemporaryFile(mode=tmp_file_mode, delete=False)

    tmp_file.write(buf)

    # Main copy loop
    while True:
        buf = file_like_object.read(16 * 1024)

        if not buf:
            break

        tmp_file.write(buf)

    return tmp_file.name


def data_to_fp(data):
    if isinstance(data, str):
        fp = StringIO()
        if six.PY2:
            data = unicode(data)  # noqa
        fp.write(data)
    elif isinstance(data, bytes):
        fp = io.BytesIO()
        fp.write(data)
    else:
        fp = StringIO()
        try:
            json.dump(data, fp)
        except Exception:
            LOGGER.error("Failed to log asset data as JSON", exc_info=True)
            return None
    fp.seek(0)
    return fp


def is_valid_file_path(file_path):
    """ Check if the given argument is corresponding to a valid file path,
    ready for reading
    """
    try:
        if os.path.isfile(file_path):
            return True
        else:
            return False
    # We can receive lots of things as arguments
    except (TypeError, ValueError):
        return False


class Histogram(object):
    """
    Data structure for holding a counts of values. Creates an
    exponentially-distributed set of bins.

    See also [`Experiment.log_histogram`](#experimentlog_histogram)
    """

    def __init__(self, start=1e-12, stop=1e20, step=1.1, offset=0):
        """
        Initialize the values of bins and data structures.

        Args:
            start: float (optional), value of start range. Default 1e-12
            stop: float (optional), value of stop range. Default 1e20
            step: float (optional), value of step. Greater than one creates an
                exponentially-distributed set of bins. Default 1.1
            offset: float (optional), center of distribution. Default is zero.
        """
        self.start = start
        self.stop = stop
        self.step = step
        self.offset = offset
        self.values = tuple(self.create_bin_values())
        self.clear()

    def clear(self):
        """
        Clear the counts, initializes back to zeros.
        """
        self.counts = [0] * len(self.values)

    def add(self, values, counts=None, max_skip_count=10):
        """
        Add the value(s) to the count bins.

        Args:
            values: a list, tuple, or array of values (any shape)
                to count
            counts: a list of counts for each value in values. Triggers
                special mode for conversion from Tensorboard
                saved format.
            max_skip_count: int, (optional) maximum number of empty
                cells that triggers a binary search.

        Counting values in bins can be expensive, so this method uses
        binary_search to find the initial bin, and iterates through
        sorted values, incrementing the bin as it goes. If too many
        bins are empty (skip_count reaches max_skip_count) then it
        jumps out and does another binary_search.
        """
        try:
            values = [float(values)]
        except Exception:
            pass

        if len(values) == 0:
            return

        # Numpy arrays have an optimized method of flattening:
        if hasattr(values, "flatten"):
            values = values.flatten()
        else:
            # Otherwise, we try to flatten via functools.reduce:
            try:
                values = functools.reduce(operator.iconcat, values, [])
            except TypeError:
                # Otherwise, assume that it is already flat:
                pass

        # Sort for speed of inserts
        if counts is None:
            values = sorted(values)
        # Find initial bin:
        bucket = self.get_bin_index(values[0])

        for i in range(len(values)):
            value = values[i]
            skip_count = 0
            while not (self.values[bucket] <= value < self.values[bucket + 1]):
                skip_count += 1
                # if too many skips
                if skip_count > max_skip_count:
                    # then let's just do a binary search
                    bucket = self.get_bin_index(value)
                    break
                else:
                    bucket += 1
            if counts is not None:
                self.counts[bucket] += int(counts[i])
            else:
                self.counts[bucket] += 1

    def counts_compressed(self):
        """
        Convert list of counts to list of [(index, count), ...].
        """
        return [
            [i, self.counts[i]] for i in range(len(self.counts)) if self.counts[i] > 0
        ]

    def to_json(self):
        """
        Return histogram as JSON-like dict.
        """
        return {
            "version": 2,
            "index_values": self.counts_compressed(),
            "values": None,
            "offset": self.offset,
            "start": self.start,
            "stop": self.stop,
            "step": self.step,
        }

    def create_bin_values(self):
        """
        Create exponentially distributed bin values
        [-inf, ..., offset - start, offset, offset + start, ..., inf)
        """
        values = [-float("inf"), self.offset, float("inf")]
        value = self.start
        while value <= self.stop:
            values.insert(1, self.offset - value)
            values.insert(-1, self.offset + value)
            value *= self.step
        return values

    def get_bin_index(self, value):
        """
        Given a value, return the bin index where:

            values[index] <= value < values[index + 1]

        Implemented using binary search.
        """
        if value == float("inf"):
            return len(self.values) - 1
        return self.binary_search(value, 0, len(self.values) - 1)

    def binary_search(self, value, low, high):
        """
        Find value between low and high, via binary search.
        """
        while True:
            middle = (high + low) // 2
            if (high - low) <= 1:
                return low
            elif value < self.values[middle]:
                high = middle
            else:
                low = middle

    def get_count(self, min_value, max_value):
        """
        Get the count (can be partial of bin count) of a range.
        """
        index = self.get_bin_index(min_value)
        current_start_value = self.values[index]
        current_stop_value = self.values[index + 1]
        count = 0
        # Add total in this area:
        count += self.counts[index]
        if current_start_value != -float("inf"):
            # Remove proportion before min_value:
            current_total_range = current_stop_value - current_start_value
            percent = (min_value - current_start_value) / current_total_range
            count -= self.counts[index] * percent
        if max_value < current_stop_value:
            # stop is inside this area too, so remove after max
            if current_start_value != -float("inf"):
                percent = (current_stop_value - max_value) / current_total_range
                count -= self.counts[index] * percent
            return count
        # max_value is beyond this area, so loop until last area:
        index += 1
        while max_value > self.values[index + 1]:
            # add the whole count
            count += self.counts[index]
            index += 1
        # finally, add the proportion in last area before max_value:
        current_start_value = self.values[index]
        current_stop_value = self.values[index + 1]
        if current_stop_value != float("inf"):
            current_total_range = current_stop_value - current_start_value
            percent = (max_value - current_start_value) / current_total_range
            count += self.counts[index] * percent
        else:
            count += self.counts[index]
        return count

    def get_counts(self, min_value, max_value, span_value):
        """
        Get the counts between min_value and max_value in
        uniform span_value-sized bins.
        """
        counts = []

        if max_value == min_value:
            max_value = min_value * 1.1 + 1
            min_value = min_value / 1.1 - 1

        bucketPos = 0
        binLeft = min_value

        while binLeft < max_value:
            binRight = binLeft + span_value
            count = 0.0
            # Don't include last as bucketLeft, which is infinity:
            while bucketPos < len(self.values) - 1:
                bucketLeft = self.values[bucketPos]
                bucketRight = min(max_value, self.values[bucketPos + 1])
                intersect = min(bucketRight, binRight) - max(bucketLeft, binLeft)

                if intersect > 0:
                    if bucketLeft == -float("inf"):
                        count += self.counts[bucketPos]
                    else:
                        count += (intersect / (bucketRight - bucketLeft)) * self.counts[
                            bucketPos
                        ]

                if bucketRight > binRight:
                    break

                bucketPos += 1

            counts.append(count)
            binLeft += span_value

        return counts

    def display(self, start, stop, step, format="%14.4f", show_empty=False):
        """
        Show counts between start and stop by step increments.

        Args:
            start: float, start of range to display
            stop: float, end of range to display
            step: float, amount to increment each range
            format: str (optional), format of numbers
            show_empty: bool (optional), if True, show all
                entries in range

        Example:

        ```
        >>> from comet_ml.utils import Histogram
        >>> import random
        >>> history = Histogram()
        >>> values = [random.random() for x in range(10000)]
        >>> history.add(values)

        Histogram
        =========
           Range Start      Range End          Count           Bins
        -----------------------------------------------------------
               -0.0000         0.1000       983.4069     [774-1041]
                0.1000         0.2000       975.5574    [1041-1049]
                0.2000         0.3000      1028.8666    [1049-1053]
                0.3000         0.4000       996.2112    [1053-1056]
                0.4000         0.5000       979.5836    [1056-1058]
                0.5000         0.6000      1010.4522    [1058-1060]
                0.6000         0.7000       986.1284    [1060-1062]
                0.7000         0.8000      1006.5811    [1062-1063]
                0.8000         0.9000      1007.7881    [1063-1064]
                0.9000         1.0000      1025.4245    [1064-1065]
        -----------------------------------------------------------
        Total:     10000.0000
        """
        counts = self.get_counts(start, stop, step)
        current = start
        total = 0.0
        next_one = current + step
        i = 0
        print("Histogram")
        print("=========")
        size = len(format % 0)
        sformat = "%" + str(size) + "s"
        columns = ["Range Start", "Range End", "Count", "Bins"]
        formats = [sformat % s for s in columns]
        print(*formats)
        print("-" * (size * 4 + 3))
        while next_one <= stop + (step) and i < len(counts):
            count = counts[i]
            total += count
            if show_empty or count > 0:
                start_bin = self.get_bin_index(current)
                stop_bin = self.get_bin_index(next_one)
                print(
                    format % current,
                    format % next_one,
                    format % count,
                    (sformat % ("[%s-%s]" % (start_bin, stop_bin))),
                )
            current = next_one
            next_one = current + step
            i += 1
        print("-" * (size * 4 + 3))
        print(("Total: " + format) % total)


def write_numpy_array_as_wav(numpy_array, sample_rate, file_object):
    """ Convert a numpy array to a WAV file using the given sample_rate and
    write it to the file object
    """
    try:
        import numpy as np
        from scipy.io.wavfile import write
    except ImportError:
        LOGGER.error(
            "The Python libraries numpy, and scipy are required for this operation"
        )
        return

    array_max = np.max(np.abs(numpy_array))

    scaled = np.int16(numpy_array / array_max * 32767)

    write(file_object, sample_rate, scaled)


def get_file_extension(file_path):
    if file_path is None:
        return None

    ext = os.path.splitext(file_path)[1]
    if not ext:
        return None

    # Get rid of the leading "."
    return ext[1::]


def encode_and_stringify(metadata):
    if metadata is None:
        return None

    if type(metadata) is not dict:
        LOGGER.info("invalid audio metadata, expecting dict type", exc_info=True)
        return None

    if metadata == {}:
        return None

    try:
        json_encoded = json.dumps(metadata, separators=(",", ":"), sort_keys=True)
        encoded = base64.urlsafe_b64encode(json_encoded.encode("utf-8")).decode("utf-8")
        return encoded
    except Exception:
        LOGGER.info(
            "invalid audio metadata, expecting JSON-encodable object", exc_info=True
        )


def get_comet_version():
    # type: () -> str
    try:
        return get_distribution("comet_ml").version
    except DistributionNotFound:
        return "Please install comet with `pip install comet_ml`"


def get_user():
    # type: () -> str
    try:
        return getpass.getuser()
    except KeyError:
        return "unknown"
