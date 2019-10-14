import itertools
import functools
import numpy

from attrs_patch import attr
from v2_dataset import units


class SpikeTrainMixin:
    """
    Required properties:
    * Compatible with :class:`v2_dataset.mixins.TimeRangeMixin`
    * timestamps
    """

    @property
    @functools.lru_cache(maxsize=None)
    def n_spikes(self):
        return len(self.timestamps)

    @property
    @functools.lru_cache(maxsize=None)
    def spike_intervals(self) -> "units.Quantity":
        """The histogram of inter-spike intervals.

        Returns
        -------
        hist:
            A vectorized quantity of (M-1) intervals, where M is the number of spikes in this unit (:attr:`n_spikes`).
        """
        sorted_instants = numpy.sort(self.timestamps) / self.sampling_rate
        return sorted_instants[1:] - sorted_instants[:-1]

    @property
    @functools.lru_cache(maxsize=None)
    def spike_times(self) -> "units.Quantity":
        """Array of spike times for this unit/channel, in unit of time.

        Return
        ------
        array:
            A vectoriezed (M,) array of spike times, where M is the number of spikes in this unit/channel.

        See also
        --------
        * :attr:`timestamps`
        """
        return (self.timestamps / self.sampling_rate).to(units.ms)

    def spike_train(self, samples=None, rate=None, period=None, endpoint=True):
        time_support = self.time_support(
            samples=samples, rate=rate, period=period, endpoint=endpoint
        )
        hist, bins = numpy.histogram(
            self.spike_times.to(time_support.u), bins=time_support
        )
        return hist


class TimeRangeMixin:
    """
    Required properties:

    * sampling_rate or sampling_period
    * start_ts (if not implemented, considered to be 0)
    * end_ts or duration_ts
    """

    @property
    def duration(self) -> "units.Quantity":
        return self.duration_ts / self.sampling_rate

    @property
    def duration_ts(self) -> int:
        return self.end_ts - self.start_ts

    @property
    def end_time(self) -> "units.Quantity":
        return self.end_ts / self.sampling_rate

    @property
    def end_ts(self) -> int:
        return self.start_ts + self.duration_ts

    @property
    def sampling_period(self) -> "units.Quantity":
        return 1 / self.sampling_rate

    @property
    def sampling_rate(self) -> "units.Quantity":
        return 1 / self.sampling_period

    @property
    def start_time(self) -> "units.Quantity":
        return self.start_ts / self.sampling_rate

    @property
    def start_ts(self) -> int:
        return 0

    def time_support(
        self, samples=None, rate=None, period=None, unit=units.ms, endpoint=True
    ) -> "units.Quantity":
        if samples is None and rate is None and period is None:
            points = self.duration_ts + int(endpoint)
        elif rate is not None:
            points = int(self.duration * rate) + int(endpoint)
        elif period is not None:
            points = int(self.duration / period) + int(endpoint)
        else:
            points = samples
        time_vector = numpy.linspace(
            self.start_time.to(unit).m,
            self.end_time.to(unit).m,
            points,
            endpoint=endpoint,
        )
        return time_vector * unit


class TrialSliceMixin:
    def __getitem__(self, trials):
        try:
            trial_list = list(trials)
        except TypeError:
            trial_list = [trials]
        sliced_proxies = []
        for trial in trial_list:
            proxy = TrialSlicer(
                spike_source=self,
                start_ts=trial.start_ts,
                duration_ts=trial.duration_ts,
            )
            sliced_proxies.append(proxy)
        if len(sliced_proxies) == 1:
            return sliced_proxies[0]
        else:
            return tuple(sliced_proxies)


@attr.s(frozen=True)
class TrialSlicer(SpikeTrainMixin, TimeRangeMixin):

    _spike_source = attr.ib()
    _start_ts = attr.ib()
    _duration_ts = attr.ib()
    # def __init__(self, spike_source, start_ts, duration_ts):
    #     self._spike_source = spike_source
    #     self.start_ts = start_ts
    #     self.duration_ts = duration_ts

    @property
    def duration_ts(self):
        return self._duration_ts

    @property
    def start_ts(self):
        return self._start_ts

    @property
    def sampling_rate(self):
        return self._spike_source.sampling_rate

    @property
    # @functools.lru_cache(maxsize=None)
    def mask(self):
        mask = numpy.bitwise_and(
            self.start_ts <= self._spike_source.timestamps,
            self._spike_source.timestamps <= self.end_ts,
        )
        return mask

    @property
    # @functools.lru_cache(maxsize=None)
    def timestamps(self):
        return self._spike_source.timestamps[self.mask]

    @property
    # @functools.lru_cache(maxsize=None)
    def waveforms(self):
        return self._spike_source.waveforms[self.mask]


class _ChannelRecordingCommon:
    @property
    def n_units(self) -> int:
        """Total number of sorted units.
        """
        return len(self.sorted_units)


class _ChannelUnitCommon(SpikeTrainMixin, TimeRangeMixin, TrialSliceMixin):
    @property
    def duration_ts(self):
        return self.spike_channel.recording.duration_ts

    @property
    @functools.lru_cache(maxsize=None)
    def n_spikes(self) -> int:
        """The total number of spikes detected for this channel/unit.
        """
        return numpy.sum(self.mask)

    @property
    def sampling_rate(self):
        return self.spike_channel.sampling_rate

    @property
    def timestamps(self) -> "numpy.ndarray":
        """Array of spike timestamps for this channel/unit, in clock ticks.

        Return
        ------
        array:
            A (M,) array of timestamps, where M is the number of spikes in this unit.

        See also
        --------
        * :attr:`times`
        """
        return self.spike_channel.timestamps[self.mask]

    @property
    def waveforms_ad(self) -> "numpy.ndarray":
        """Array of unit waveforms (in A/D space).

        Return
        ------
        array:
            A (M, N) array of M waveforms, with N samples (A/D) each.
        """
        return self.spike_channel.waveforms[self.mask]


class SortedChannel(_ChannelUnitCommon, _ChannelRecordingCommon):
    """Convenience snippets (properties/methods) for :class:`v2.sorting.ifs.SortedChannel` objects.
    """

    @property
    def algorithm(self):
        return self.sorting.algorithm

    @property
    def unsorted_mask(self):
        return ~self.mask


class SortedRecording(_ChannelRecordingCommon):
    """Convenience snippets (properties/methods) for :class:`v2.sorting.ifs.SortedRecording` objects.
    """

    @property
    def sorted_units(self) -> "Sequence[SortedUnit]":
        """Access to all sorted units obtained by the corresponding sorting process."""
        sorted_units = list(
            itertools.chain(*[channel.sorted_units for channel in self.sorted_channels])
        )
        return sorted_units


class SortedUnit(_ChannelUnitCommon):
    """Convenience snippets (properties/methods) for :class:`v2.sorting.ifs.SortedUnit` objects.
    """

    @property
    def algorithm(self):
        """Shortcut for :code:`unit.sorted_channel.algorithm`.
        """
        return self.sorted_channel.algorithm

    @property
    @functools.lru_cache(maxsize=None)
    def mask(self):
        return self.sorted_channel.spike_labels == self.label

    @property
    def spike_channel(self):
        """Shortcut for :code:`unit.sorted_channel.spike_channel`.
        """
        return self.sorted_channel.spike_channel

    @property
    @functools.lru_cache(maxsize=None)
    def waveform_ad_mean(self):
        """Compute the mean waveform as the sample-wise mean of all waveforms in this unit.

        Returns
        -------
        waveform: numpy.ndarray
            An (N,) array of waveform A/D samples.
        """
        return numpy.mean(self.waveforms_ad, axis=0)

    @property
    @functools.lru_cache(maxsize=None)
    def waveform_ad_std(self):
        """Compute the waveform deviation as the sample-wise standard-deviation of all waveforms in this unit.

        Returns
        -------
        waveform: numpy.ndarray
            An (N,) array of waveform A/D samples.
        """
        return numpy.std(self.waveforms_ad, axis=0)
