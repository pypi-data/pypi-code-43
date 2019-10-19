# -*- coding: utf-8 -*-
# Copyright (c) 2019 by Lars Klitzke, Lars.Klitzke@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import argparse
import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from multiprocessing import Manager
from shutil import copyfile
from threading import Thread, Lock
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tqdm
from colorlog import colorlog

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))), 'data')


def set_data_dir(directory):
    """
    Set the data directory

    Args:
        directory (str):    The path to the data directory.
    """
    global DATA_DIR

    DATA_DIR = directory


def data_dir(name):
    """
    Get the default data directory next to the notebooks.

    Args:
        name (str): Name of the data file

    Returns:
        str: Path to the data file in the data directory.

    """

    return os.path.join(DATA_DIR, name)


class TqdmQueue(object):
    """
    This is a queue for using Tqdm progressbars in a multiprocessing environment
    """

    def __init__(self, queue):
        self.q = queue

    def update_progress(self, progress, total):
        """
        Update the progress

        Args:
            progress (int|float):   The current iteration number
            total (int|float):      The total number of iterations

        Returns:

        """
        self.q.put((os.getpid(), TqdmManager.TqdmCommand.UPDATE, (progress, total)))

    def write(self, text):
        """
        Write the given text to the console using tqdm.

        Args:
            text (str): Any text to log
        """
        self.q.put((os.getpid(), TqdmManager.TqdmCommand.WRITE, text))

    def reset(self):
        """
        Reset the progress bar
        """
        self.q.put((os.getpid(), TqdmManager.TqdmCommand.RESET, None))

    def get(self, *args, **kwargs):
        return self.q.get(*args, **kwargs)

    def close(self):
        self.q.put(None)


class TqdmManager(Thread):
    class TqdmCommand(Enum):
        UPDATE = 'update'
        WRITE = 'write'
        RESET = 'reset'

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Two lists for new connected clients and already registered ones
        self.new_client_queues = []  # type: list[TqdmQueue]
        self.registered_client_queues = []  # type: list[TqdmQueue]

        # Two lists for the progress bar configurations
        self.new_pbar_config = []
        self.registered_pbar_config = []

        self.lock = Lock()

        # This is a list of thread for updating the progress bars
        self.threads = []

        # For Queue management
        self._manager = Manager()

        self._should_stop = False

    def connect(self, **kwargs):
        """
        Connect to the TqdmManager
        Args:
            **kwargs:

        Returns:
            TqdmQueue:  The queue for updating the progress bar

        """
        if 'positions' in kwargs:
            del kwargs['position']

        # create the queue for updating the progress bar
        client_queue = TqdmQueue(self._manager.Queue())

        with self.lock:
            self.new_client_queues.append(client_queue)
            self.new_pbar_config.append(kwargs)

        return client_queue

    def stop(self):
        self._should_stop = True

    def run(self):

        def update_progressbar_thread(queue, pbar_config, idx):

            progressbar = None  # type: tqdm.tqdm
            try:
                while True:
                    pid, cmd, value = queue.q.get()  # type: int, int, int

                    if cmd is TqdmManager.TqdmCommand.UPDATE:

                        progress, total = value

                        if progressbar is None:
                            # initialize the progress bar
                            progressbar = tqdm.tqdm(position=idx, total=total, **pbar_config)

                        progressbar.update()

                    elif cmd is TqdmManager.TqdmCommand.WRITE:
                        if progressbar is not None:
                            progressbar.write(value)
                        else:
                            print(value)
                    elif cmd is TqdmManager.TqdmCommand.RESET:
                        if progressbar is not None:
                            progressbar = None

            except TypeError:
                pass
            finally:
                progressbar.close()

        while not self._should_stop:

            # create a local copy for thread-safeness and cleanup the list of new connections
            with self.lock:
                ncq, npbc = self.new_client_queues, self.new_pbar_config

                self.new_client_queues, self.new_pbar_config = [], []

            for q, pbc in zip(ncq, npbc):
                # add the new queue to the registered ones
                self.registered_client_queues.append(q)
                # and the config
                self.registered_pbar_config.append(pbc)

                # create a new thread for updating the progress bar for that client
                t = Thread(target=update_progressbar_thread, args=(q, pbc, len(self.registered_pbar_config) - 1))
                t.start()

                self.threads.append(t)

            sleep(1)

        # close all queues and wait for the threads to finish
        for queue, thread in zip(self.registered_client_queues, self.threads):
            queue.close()

            thread.join()


class TqdmLoggingHandler(logging.Handler):
    def __init__(self, tqdm_queue, level=logging.NOTSET):
        super().__init__(level)

        self._queue = tqdm_queue

        self.setFormatter(
            colorlog.ColoredFormatter(
                '%(log_color)s[%(asctime)s | %(filename)s:%(funcName)s:%(lineno)d] '
                '<%(processName)s:%(process)d: %(threadName)s> %(levelname)s:%(message)s',
                datefmt='%Y-%d-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'white',
                    'SUCCESS:': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white'}, )
        )

    def emit(self, record):
        try:
            msg = self.format(record)

            self._queue.write(msg)
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class PlotWriter(object):

    def __init__(self, directory):
        """
        Args:
            directory (str): Path to the directory to write the plots itno
        """

        os.makedirs(directory, exist_ok=True)

        self._directory = directory

    def save(self, name, **kwargs):
        """
        Save the current figure into a file

        Args:
            name:       The name of the file
            **kwargs:   see the keyword arguments of matplotlib.savefig


        Returns:

        """

        if 'fname' in kwargs:
            del kwargs['fname']

        fig = save_figure(os.path.join(self._directory, name), **kwargs)

        for a in fig.axes:
            a.clear()


def save_figure(name, fig=None, encodings=('png', 'pdf'), **kwargs):
    """
    Save the given figure or the current one to disk.

    Args:
        name (str):             Name of the file
        fig (plt.Figure):       The figure to save
        encodings (tuple[str]): A list of encoding names. By default, the figure will be saved as .pdf and .png file.

    Returns:
        plt.Figure:     The saved figure
    """

    if fig is None:
        fig = plt.gcf()

    # check if the destination directory exists
    dir_path = os.path.dirname(os.path.abspath(name))

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    encoding_params = {
        'bbox_inches': 'tight', 'dpi': 300
    }
    for encoding in encodings:

        args = encoding_params.copy()

        if kwargs:
            args.update(**kwargs)

        fig.savefig('{name}.{encoding}'.format(name=name, encoding=encoding), **args)

    return fig


def format_datetime(timestamp):
    """
    Format the timestamp as a string in the correct format used throughout this project.

    Args:
        timestamp (datetime|str): The datetime as datetime object

    Returns:
        str|datetime:    The datetime as string or datetime object
    """
    if isinstance(timestamp, datetime):
        return timestamp.strftime(DATETIME_FORMAT)
    elif isinstance(timestamp, str):
        return datetime.strptime(timestamp, DATETIME_FORMAT)


def save_dataframe(df, timestamp, directory, postfix=''):
    """
    Save the pandas DataFrame to disk.

    Args:
        df (pd.DataFrame):      The pandas DataFrame to save to disk.
        timestamp (str):   The timestamp for name generation
        directory (str):        The directory to save the matrix into
        postfix (str):             Optional suffix of the final name

    Returns:

    """

    os.makedirs(directory, exist_ok=True)

    if '.csv' not in postfix:
        postfix += '.csv'

    path = os.path.join(directory, "{}{}".format(timestamp, postfix))

    logging.debug('Save pandas dataframe to %s', path)

    df.to_csv(path)

    return path


def save_ndarray(arr, timestamp, directory, postfix=''):
    """
    Save the array into the directory.

    Args:
        arr (np.ndarray):       A numpy array
        timestamp (datetime):   The timestamp for name generation
        directory (str):        The directory to save the matrix into
        postfix (str):          Optional postfix of the final name
    """

    os.makedirs(directory, exist_ok=True)

    path = os.path.join(directory, "{}{}".format(format_datetime(timestamp), postfix))

    np.save(path, arr)

    logging.debug('Save numpy array to %s', path)

    return path + ".npy"


def load_ndarray(directory, timestamp, postfix=''):
    """
    Load the array from the given path.

    Args:
        timestamp (datetime):   The timestamp for name generation
        directory (str):        The directory of the the matrix into
        postfix (str):          Optional postfix of the final name

    Returns:
        np.ndarray: The array

    """
    path = os.path.join(directory, "{}{}.npy".format(format_datetime(timestamp), postfix))

    logging.debug('Load numpy array from %s', path)

    arr = np.load(path)

    return arr


def load_ground_truth(sequence_name, **kwargs):
    """
    Load the ground truth data of the sequence with the given name.

    Args:
        sequence_name (str): The name of the sequence

    Returns:
        pandas.DataFrame: The ground truth data as a pandas `DataFrame`
    """

    df = load_dataframe(data_dir('ground_truth'), sequence_name, **kwargs)

    return df


def load_dataframe(directory, name, postfix='', **kwargs):
    """
    Load a dataframe from the directory with the given name.

    Args:
        directory (str):    Directory to load the dataframe from
        name (str)          Name of the dataframe
        postfix (str):      An optional postfix

    Returns:
        pd.DataFrame: The dataframe as pandas DataFrame.

    """

    file = os.path.join(directory, "{}{}".format(name, postfix))

    if '.csv' not in file:
        file += '.csv'

    logging.debug('Load pandas dataframe from %s', file)

    df = pd.read_csv(file, **kwargs)

    if 'timestamp' in df:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    return df


def rename_images(directory, destination = None, interval=None):
    """
    Rename the images in the given directory

    Args:
        directory (str):        The directory with images
        destination (str|None): An optional directory to copy the renamed images into
        interval (int|None):    The copy time interval in microseconds

    Yields:
        tuple[int, int]:        The number of processed and available images
    """

    # convert the interval to a timedelta object
    if interval:
        interval = timedelta(microseconds=int(interval))
    else:
        interval = timedelta(microseconds=0)

    os.makedirs(destination, exist_ok=True)

    last_time = None

    files = os.listdir(directory)

    num_files = len(files)
    for idx, file in enumerate(sorted(files)):

        timestamp, serial, ext = file.split('_')

        timestamp = datetime.utcfromtimestamp(int(timestamp) / 1E6)

        if last_time is None or interval <= (timestamp - last_time):
            last_time = timestamp

            if destination:
                # copy the renamed file
                copyfile(os.path.join(directory, file),
                         os.path.join(destination, "{}_{}_{}".format(timestamp.isoformat(), serial, ext)))
            else:
                # do not copy but rename
                os.rename(os.path.join(directory, file),
                          os.path.join(directory, "{}_{}_{}".format(timestamp.isoformat(), serial, ext)))

        yield idx, num_files


def to_epoch(timestamp):
    """
    Convert the given timestamp assumed in UTC to epoch time in seconds

    Args:
        timestamp (datetime):   A valid datetime

    Returns:
        float:  The epoch time in seconds

    """
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=None)

    timestamp = timestamp.replace(tzinfo=None)
    # remove the timezone information - both datetimes are actually in UTC
    return int((timestamp - epoch).total_seconds() * 1000000)


def entry_image_rename():
    """
    Entry point for image renaming
    """
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('--log-level', help='''
            defines which messages should be logged (INFO, DEBUG, WARNING, ERROR).
            For further modes see the logging class.
            ''', default='INFO', choices=['INFO', 'DEBUG', 'WARNING', 'ERROR'])

    arg_parser.add_argument('--directory', help="Path to images to rename", required=True)

    arg_parser.add_argument('--destination', help="Where to save the renamed images.", required=False, default=None)

    arg_parser.add_argument('--interval', help="Renaming interval in microseconds", required=False, default=None)

    arguments = arg_parser.parse_args()

    pbar = None

    for idx, total in rename_images(directory=arguments.directory,
                                    destination=arguments.destination,
                                    interval=arguments.interval):

        if pbar is None:
            pbar = tqdm.tqdm(total=total, desc='Renamed images', unit='image')

        pbar.update()

    pbar.close()

