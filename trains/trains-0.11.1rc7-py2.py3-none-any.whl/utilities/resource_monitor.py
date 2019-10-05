import logging
import warnings
from time import time
from threading import Thread, Event

import psutil
from pathlib2 import Path
from typing import Text
from ..binding.frameworks.tensorflow_bind import IsTensorboardInit

try:
    from .gpu import gpustat
except ImportError:
    gpustat = None


class ResourceMonitor(object):
    _title_machine = ':monitor:machine'
    _title_gpu = ':monitor:gpu'

    def __init__(self, task, sample_frequency_per_sec=2., report_frequency_sec=30.,
                 first_report_sec=None, wait_for_first_iteration_to_start_sec=180.0,
                 max_wait_for_first_iteration_to_start_sec=1800.):
        self._task = task
        self._sample_frequency = sample_frequency_per_sec
        self._report_frequency = report_frequency_sec
        self._first_report_sec = first_report_sec or report_frequency_sec
        self._wait_for_first_iteration = wait_for_first_iteration_to_start_sec
        self._max_check_first_iteration = max_wait_for_first_iteration_to_start_sec
        self._num_readouts = 0
        self._readouts = {}
        self._previous_readouts = {}
        self._previous_readouts_ts = time()
        self._thread = None
        self._exit_event = Event()
        self._gpustat_fail = 0
        self._gpustat = gpustat
        if not self._gpustat:
            self._task.get_logger().report_text('TRAINS Monitor: GPU monitoring is not available')

    def start(self):
        self._exit_event.clear()
        self._thread = Thread(target=self._daemon)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._exit_event.set()
        # self._thread.join()

    def _daemon(self):
        logger = self._task.get_logger()
        seconds_since_started = 0
        reported = 0
        last_iteration = 0
        fallback_to_sec_as_iterations = None
        # last_iteration_interval = None
        # last_iteration_ts = 0
        # repeated_iterations = 0
        while True:
            last_report = time()
            current_report_frequency = self._report_frequency if reported != 0 else self._first_report_sec
            while (time() - last_report) < current_report_frequency:
                # wait for self._sample_frequency seconds, if event set quit
                if self._exit_event.wait(1.0 / self._sample_frequency):
                    return
                # noinspection PyBroadException
                try:
                    self._update_readouts()
                except Exception:
                    pass

            seconds_since_started += int(round(time() - last_report))
            # check if we do not report any metric (so it means the last iteration will not be changed)
            if fallback_to_sec_as_iterations is None:
                if IsTensorboardInit.tensorboard_used():
                    fallback_to_sec_as_iterations = False
                elif seconds_since_started >= self._wait_for_first_iteration:
                    self._task.get_logger().report_text('TRAINS Monitor: Could not detect iteration reporting, '
                                                        'falling back to iterations as seconds-from-start')
                    fallback_to_sec_as_iterations = True
            elif fallback_to_sec_as_iterations is True and seconds_since_started <= self._max_check_first_iteration:
                if self._check_logger_reported():
                    fallback_to_sec_as_iterations = False
                    self._task.get_logger().report_text('TRAINS Monitor: Reporting detected, '
                                                        'reverting back to iteration based reporting')

            clear_readouts = True
            # if we do not have last_iteration, we just use seconds as iteration
            if fallback_to_sec_as_iterations:
                iteration = seconds_since_started
            else:
                iteration = self._task.get_last_iteration()
                if iteration < last_iteration:
                    # we started a new session?!
                    # wait out
                    clear_readouts = False
                    iteration = last_iteration
                elif iteration == last_iteration:
                    # repeated_iterations += 1
                    # if last_iteration_interval:
                    #     # to be on the safe side, we don't want to pass the actual next iteration
                    #     iteration += int(0.95*last_iteration_interval[0] * (seconds_since_started - last_iteration_ts)
                    #                      / last_iteration_interval[1])
                    # else:
                    #     iteration += 1
                    clear_readouts = False
                    iteration = last_iteration
                else:
                    # last_iteration_interval = (iteration - last_iteration, seconds_since_started - last_iteration_ts)
                    # repeated_iterations = 0
                    # last_iteration_ts = seconds_since_started
                    last_iteration = iteration
                    fallback_to_sec_as_iterations = False
                    clear_readouts = True

            # start reporting only when we figured out, if this is seconds based, or iterations based
            average_readouts = self._get_average_readouts()
            if fallback_to_sec_as_iterations is not None:
                for k, v in average_readouts.items():
                    # noinspection PyBroadException
                    try:
                        title = self._title_gpu if k.startswith('gpu_') else self._title_machine
                        # 3 points after the dot
                        value = round(v*1000) / 1000.
                        logger.report_scalar(title=title, series=k, iteration=iteration, value=value)
                    except Exception:
                        pass
                # clear readouts if this is update is not averaged
                if clear_readouts:
                    self._clear_readouts()

            # count reported iterations
            reported += 1

    def _update_readouts(self):
        readouts = self._machine_stats()
        elapsed = time() - self._previous_readouts_ts
        self._previous_readouts_ts = time()
        for k, v in readouts.items():
            # cumulative measurements
            if k.endswith('_mbs'):
                v = (v - self._previous_readouts.get(k, v)) / elapsed

            self._readouts[k] = self._readouts.get(k, 0.0) + v
        self._num_readouts += 1
        self._previous_readouts = readouts

    def _get_num_readouts(self):
        return self._num_readouts

    def _get_average_readouts(self):
        average_readouts = dict((k, v/float(self._num_readouts)) for k, v in self._readouts.items())
        return average_readouts

    def _clear_readouts(self):
        self._readouts = {}
        self._num_readouts = 0

    def _machine_stats(self):
        """
        :return: machine stats dictionary, all values expressed in megabytes
        """
        cpu_usage = [float(v) for v in psutil.cpu_percent(percpu=True)]
        stats = {
            "cpu_usage": sum(cpu_usage) / float(len(cpu_usage)),
        }

        bytes_per_megabyte = 1024 ** 2

        def bytes_to_megabytes(x):
            return x / bytes_per_megabyte

        virtual_memory = psutil.virtual_memory()
        stats["memory_used_gb"] = bytes_to_megabytes(virtual_memory.used) / 1024
        stats["memory_free_gb"] = bytes_to_megabytes(virtual_memory.available) / 1024
        disk_use_percentage = psutil.disk_usage(Text(Path.home())).percent
        stats["disk_free_percent"] = 100.0-disk_use_percentage
        with warnings.catch_warnings():
            if logging.root.level > logging.DEBUG:  # If the logging level is bigger than debug, ignore
                # psutil.sensors_temperatures warnings
                warnings.simplefilter("ignore", category=RuntimeWarning)
            sensor_stat = (psutil.sensors_temperatures() if hasattr(psutil, "sensors_temperatures") else {})
        if "coretemp" in sensor_stat and len(sensor_stat["coretemp"]):
            stats["cpu_temperature"] = max([float(t.current) for t in sensor_stat["coretemp"]])

        # update cached measurements
        net_stats = psutil.net_io_counters()
        stats["network_tx_mbs"] = bytes_to_megabytes(net_stats.bytes_sent)
        stats["network_rx_mbs"] = bytes_to_megabytes(net_stats.bytes_recv)
        io_stats = psutil.disk_io_counters()
        stats["io_read_mbs"] = bytes_to_megabytes(io_stats.read_bytes)
        stats["io_write_mbs"] = bytes_to_megabytes(io_stats.write_bytes)

        # check if we can access the gpu statistics
        if self._gpustat:
            try:
                gpu_stat = self._gpustat.new_query()
                for i, g in enumerate(gpu_stat.gpus):
                    stats["gpu_%d_temperature" % i] = float(g["temperature.gpu"])
                    stats["gpu_%d_utilization" % i] = float(g["utilization.gpu"])
                    stats["gpu_%d_mem_usage" % i] = 100. * float(g["memory.used"]) / float(g["memory.total"])
                    # already in MBs
                    stats["gpu_%d_mem_free_gb" % i] = float(g["memory.total"] - g["memory.used"]) / 1024
                    stats["gpu_%d_mem_used_gb" % i] = float(g["memory.used"]) / 1024
            except Exception:
                # something happened and we can't use gpu stats,
                self._gpustat_fail += 1
                if self._gpustat_fail >= 3:
                    self._task.get_logger().report_text('TRAINS Monitor: GPU monitoring failed getting GPU reading, '
                                                        'switching off GPU monitoring')
                    self._gpustat = None

        return stats

    def _check_logger_reported(self):
        titles = list(self._task.get_logger()._get_used_title_series().keys())
        try:
            titles.remove(self._title_machine)
        except ValueError:
            pass
        try:
            titles.remove(self._title_gpu)
        except ValueError:
            pass
        return len(titles) > 0
