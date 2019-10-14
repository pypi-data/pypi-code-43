"""All model classes define a convenience class-method ``query``, which is in fact a shortcut to calling
:meth:`v2_dataset.db.ScopedSession.query` with that class passed as the first argument.
"""

import datetime
import textwrap

import dateutil
import enum
import json
import numpy
import pathlib

from .base import Model
from attrs_patch import attr
from compneuro import kernels, signal
from v2_dataset import config, units
from v2_dataset.orm import Column, StrictForeignKey, mixins, relationship, types
from v2_dataset.mixins import SpikeTrainMixin, TimeRangeMixin, TrialSliceMixin
from sqlalchemy import CheckConstraint, UniqueConstraint, and_, or_
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import backref

#: Trial condition codes common to all types of stimulus.
_common_condition_codes = {
    "PLX_START": (258, "Corresponds to timestamp 0."),
    "PLX_STOP": (259, "Corresponds to the last timestamp recorded in the file."),
    "PROTOCOL_START": (255, "All ordinary condition codes follow this code."),
    "PROTOCOL_STOP": (254, "All ordinary condition codes precede this code."),
}


def _create_enum(name, base_attrs, more_attrs={}, docstring="", module=None):
    """A helper function for creating a enumeration types for stimulus conditions.

    This function is a helper around :mod:`enum`'s functional API, and its invocation roughly corresponds to

        >>> import enum
        >>> new_type = enum.Enum(
        ...    name,
        ...    { key: val[0] for key, val in dict({**base_attrs, **more_attrs}).items() },
        ...    module=module
        ... )

    with the addition that it also uses ``val[1]`` for setting enumeration constant docstrings, and sets the new type's
    docstring itself.

    Parameters
    ----------
    name: str
        Name of new type.

    base_attrs: dict
        A dictionary of enumeration constants. The keys should be the names of the constants, and the values should
        be tuples where the first element is the constant's value, and the second is its docstring.

    more_attrs: dict, optional
        Additional enumeration constants.

    docstring: str, optional
        The new type's docstring.

    module: str, optional
        The name of the module the new type will belong to. May be needed for correct pickling, according to Python's
        docs on the :mod:`enum` module.
    """

    class Mixin:
        @classmethod
        def stimulus_variations(cls):
            """Return a list of the enumeration values that correspond to stimulus variations.

            Returns
            -------
            list
            """
            return [cls[const] for const in more_attrs]

    attrs = {key: val[0] for key, val in base_attrs.items()}
    attrs.update({key: val[0] for key, val in more_attrs.items()})

    if module:
        enum_type = enum.Enum(name, attrs, module=module, type=Mixin)
    else:
        enum_type = enum.Enum(name, attrs, type=Mixin)

    enum_type.__doc__ = docstring

    for key in base_attrs:
        getattr(enum_type, key).__doc__ = base_attrs[key][1]

    for key in more_attrs:
        getattr(enum_type, key).__doc__ = more_attrs[key][1]

    return enum_type


@attr.autodoc
@attr.s(frozen=True)
class MeaDepth:
    left: units.Quantity = attr.ib(
        metadata={"help": "Insertion depth on left hemisphere."}
    )
    right: units.Quantity = attr.ib(
        metadata={"help": "Insertion depth on right hemisphere."}
    )


@attr.autodoc
@attr.s(frozen=True)
class MeaLayout:
    rows: int = attr.ib(converter=int, metadata={"help": "Electrodes per row."})
    cols: int = attr.ib(converter=int, metadata={"help": "Electrodes per column."})


@attr.s(frozen=True)
class OriginalPath:
    directory: str = attr.ib(converter=str)
    filename: str = attr.ib(converter=str)


@attr.autodoc
@attr.s(frozen=True)
class WaveformSamplingProperties:
    """Namespace object that contains information on how waveform clips originated from spike channels in a *PLX* file
    are recorded.

    Note
    ----
    These properties are also accessible from the :class:`v2.db.model.SpikeChannel` class for convenience, although
    they have common values for all spike channels associated with the same :class:`v2.db.model.Recording` object.
    """

    samples: int = attr.ib(converter=int, metadata={"help": "Total number of samples."})
    samples_pre_thr: int = attr.ib(
        converter=int,
        metadata={"help": "Number of samples prior to threshold crossing."},
    )
    sampling_rate: units.Quantity = attr.ib(
        converter=units.Quantity, metadata={"help": "Rate at which samples are taken."}
    )

    @property
    def duration(self):
        """Elapsed time between first and last samples.

        :rtype: v2_dataset.units.Quantity
        """
        return (self.samples - 1) / self.sampling_rate

    @property
    def sample_interval(self):
        """Time interval between consecutive samples.

        :rtype: v2_dataset.units.Quantity
        """
        return 1 / self.sampling_rate

    @property
    def samples_post_thr(self):
        """Number of samples after threshold (including time of threshold).

        :rtype: int
        """
        return self.num_points - self.num_points_pre_thr

    @property
    def threshold_time(self):
        """The time instant, relative to waveform start, at which threshold occurs.

        :rtype: v2_dataset.units.Quantity
        """
        return self.samples_pre_thr * self.sample_interval


CommonConditions = _create_enum(
    name="CommonConditions",
    base_attrs=_common_condition_codes,
    more_attrs={},
    docstring="Common condition codes that may be found in all PLX files in the dataset.",
    module=__name__,
)
MovingBarConditions = _create_enum(
    name="MovingBarConditions",
    base_attrs=_common_condition_codes,
    more_attrs={
        "ORIENT_0_DEG": (1, "Oriented at zero degrees."),
        "ORIENT_45_DEG": (2, "Oriented at 45 degrees."),
        "ORIENT_90_DEG": (3, "Oriented at 90 degrees."),
        "ORIENT_135_DEG": (4, "Oriented at 135 degrees."),
        "ORIENT_180_DEG": (5, "Oriented at 180 degrees."),
        "ORIENT_225_DEG": (6, "Oriented at 225 degrees."),
        "ORIENT_270_DEG": (7, "Oriented at 270 degrees."),
        "ORIENT_315_DEG": (8, "Oriented at 315 degrees."),
    },
    docstring="Condition codes for experiments with moving bar stimulus",
    module=__name__,
)
GratingConditions = _create_enum(
    name="GratingConditions",
    base_attrs=_common_condition_codes,
    more_attrs={
        f"GRATING_{code}": (code, f"Grating with 8 channel-to-bit decoded value {code}")
        for code in range(1, 106)
    },
    docstring=textwrap.dedent(
        """Condition codes for experiments with grating stimuli.

        Notes
        -----
        This is a temporary implementation, based on the scarce evidence provided by *PLX* file 226 about how stimulus
        conditions are encoded. In that file, decoding condition codes assuming an 8 channel-to-bit encoding similar to
        moving bar stimuli, we get 10 repetitions of each of the sequential integers 1..105 (inclusive).
        """
    ),
    module=__name__,
)


class CytoxBand(enum.Enum):
    """Indicates the type of Cytochrome Oxidase (CytOx) band an electrode (:class:`v2.db.model.Electrode`) was pushed
    into.
    """

    INTERBAND1 = "inter-bands type 1"
    INTERBAND2 = "inter-bands type 2"
    THICK = "thick band"
    THIN = "thin band"
    UNKNOWN = "unknown"


class Hemisphere(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    UNKNOWN = "unknown"


class RecordingTrodalness(enum.Enum):
    # .. todo:: Move this class to :mod:`plx.parsing`.
    SINGLE = 1
    STEREOTRODE = 2
    TETRODE = 4


class Stimulus(enum.Enum):
    """This enumeration describes known stimulus values in the dataset.

    .. attribute:: conditions_type type

        Maps to an enumeration type in this module (*e.g.* :class:`MovingBarConditions`, or :class:`GratingConditions`)
        that describes the experimental conditions for the corresponding stimulus type.
    """

    BLACK = ("BLACK", None)
    BLACK_1 = ("BLACK_1", None)
    BLACK_68 = ("BLACK_68", None)
    BLACK_COL = ("BLACK_COL", None)
    BLACK_COL_1 = ("BLACK_COL_1", None)
    COL = ("COL", None)
    COL_1 = ("COL_1", None)
    COL_68 = ("COL_68", None)
    CON = ("CON", None)
    CONTRAST = ("CONTRAST", None)
    CON_1 = ("CON_1", None)
    CON_68 = ("CON_68", None)
    ELETRO = ("ELETRO", None)
    GRATING = ("GRATING", GratingConditions)
    MB = ("MB", MovingBarConditions)

    def __init__(self, name, conditions_type):
        self.conditions_type = conditions_type


class MEA(Model, mixins.PrimaryKey):
    """Represents a multi-electrode array (MEA) assembly.
    """

    rows = Column(types.Integer, nullable=False)
    cols = Column(types.Integer, nullable=False)
    spacing_mm = Column(types.Float)
    comment = Column(types.String)

    __table_args__ = (
        UniqueConstraint(rows, cols, spacing_mm),
        CheckConstraint(and_(rows > 0, cols > 0)),
        CheckConstraint(spacing_mm > 0),
    )

    @property
    def height(self):
        return self.height_mm * units.mm

    @hybrid_property
    def height_mm(self):
        return self.cols * self.spacing_mm

    @property
    def total_area(self):
        return self.total_area_mm2 * units.mm ** 2

    @hybrid_property
    def total_area_mm2(self):
        return self.width_mm * self.height_mm

    @hybrid_property
    def total_electrodes(self):
        return self.rows * self.cols

    @property
    def width_mm(self):
        return self.width_mm * units.mm

    @hybrid_property
    def width_mm(self):
        return self.cols * self.spacing_mm


class Subject(Model):
    """One of the four test-subjects from the original V2 dataset."""

    name = Column(types.String, primary_key=True, nullable=False)
    species = Column(types.String, nullable=False)
    comment = Column(types.String)


class RecordingSession(Model, mixins.PrimaryKey):
    """A sequence of recordings of a test subject, usually comprised of several recordings with different stimuli.

    The relationship between :class:`RecordingSession` and :class:`PlxFile` is 1-to-N.
    """

    #: Test subject.
    subject_name = Column(types.String, StrictForeignKey(Subject.name), nullable=False)

    #: Description of session.
    comment = Column(types.String)

    #: Electrode array inserted on left hemisphere.
    mea_left_id = Column(types.Integer, StrictForeignKey(MEA.id), nullable=True)

    #: Electrode array inserted on right hemisphere.
    mea_right_id = Column(types.Integer, StrictForeignKey(MEA.id), nullable=True)

    __table_args__ = (CheckConstraint(or_(mea_left_id != None, mea_right_id != None)),)

    @property
    def duration(self):
        return self.end_datetime - self.start_datetime

    @hybrid_property
    def end_datetime(self):
        return self.recordings[-1].date_time

    @hybrid_property
    def start_datetime(self):
        return self.recordings[0].date_time


class Electrode(Model, mixins.PrimaryKey):
    channel = Column(types.Integer, nullable=False)
    session_id = Column(
        types.Integer, StrictForeignKey(RecordingSession.id), nullable=False
    )
    hemisphere = Column(
        types.Enum(Hemisphere), nullable=False, default=Hemisphere.UNKNOWN
    )
    cytox_band = Column(
        types.Enum(CytoxBand), nullable=False, default=CytoxBand.UNKNOWN
    )

    __table_args__ = (UniqueConstraint(channel, session_id, hemisphere),)


class Recording(Model, TimeRangeMixin):
    """A recording session, consisting in the presentation of a single stimulus at a fixed depth, stored in a PLX file.

    The relationship between :class:`RecordingSession` and :class:`PlxFile` is 1-to-N.
    """

    id = Column(types.Integer, primary_key=True)

    #: Corresponding recording session.
    #:
    #: .. seealso:: Relationship :attr:`session`
    session_id = Column(
        types.Integer, StrictForeignKey(RecordingSession.id), nullable=False
    )

    #: Points to a recording that supposedly replaces this one (because of errors or poor recording quality).
    #:
    #: .. seealso:: Relationship :attr:`repeated_by`
    repeated_by_id = Column(types.Integer, StrictForeignKey(id))

    #: Indicates that this recording is actually an embedded sorting version of another recording. Usually, in these
    #: cases, either the associated PLX files have identical sizes (therefore differing only in unit discrimination), or
    #: slow channel information has been wiped out of the sorted recording's PLX file.
    sorting_of_id = Column(types.Integer, StrictForeignKey(id))

    #: Maximum number of sorted units this file seems to feature (derived from PLX counts section).
    max_units = Column(types.Integer, nullable=False)

    #: File size, in bytes.
    size_bytes = Column(types.Integer, nullable=False)

    # .. todo:: Replace by an enum-class or Stimulus-entity reference, in the future
    #: Indicates which stimulus was presented during this recording.
    stimulus = Column(types.Enum(Stimulus), nullable=False)

    #: Depth of electrode array insertion on left hemisphere. Null values indicate no recording in this hemisphere.
    depth_left_um = Column(types.Integer)

    #: Depth of electrode array insertion on right hemisphere. Null values indicate no recording in this hemisphere.
    depth_right_um = Column(types.Integer)

    # .. todo:: Check the value of this field in all files by verifying the number of exported spike channels.
    #: Number of spike/slow waveform channel headers that seem to have been actually recorded.
    apparent_ad_headers = Column(types.Integer, nullable=False)

    #: Number of event channels that seem to have been actually recorded.
    apparent_event_headers = Column(types.Integer, nullable=False)

    #: Additional fields from the automatic parsing of file names.
    parsing_details = Column(types.String)

    #: 32-byte MD5 digest of the PLX file, represented as 8-bit ASCII characters.
    md5_sum = Column(types.String(32), nullable=False)

    #: PLX version. Information derived from file header.
    plx_version = Column(types.Integer, nullable=False)

    #: Recording comment. Information derived from file header.
    plx_comment = Column(types.String(128))

    #: Sampling rate of A/D (spike and slow waveform) channels, in hertz. Information derived from file header.
    #:
    #: .. seealso:: Attributes :attr:`WaveformFreq`, :attr:`ad_frequency`, :attr:`waveform_freq`
    plx_ad_frequency = Column(types.Integer, nullable=False)

    #: Number of spike channels described in headers (not necessarily recorded). Information derived from file header.
    plx_num_dsp_channels = Column(types.Integer, nullable=False)

    #: Number of event channels described in headers (not necessarily recorded). Information derived from file header.
    plx_num_event_channels = Column(types.Integer, nullable=False)

    #: Number of slow waveform channels described in headers (not necessarily recorded). Information derived from file
    #: header.
    plx_num_slow_channels = Column(types.Integer, nullable=False)

    #: Number of waveform samples recorded for each spike. Information derived from file header.
    plx_num_points_wave = Column(types.Integer, nullable=False)

    #: Number of waveform samples that preceed spike threshold. Information derived from file header.
    plx_num_points_pre_thr = Column(types.Integer, nullable=False)

    #: Recording date (GMT-3). Information derived from file header.
    #:
    #: .. seealso:: Attributes :attr:`date`
    plx_date = Column(types.Date, nullable=False)

    #: Recording time (GMT-3). Information derived from file header.
    #:
    #: .. seealso:: Attributes :attr:`date`
    plx_time = Column(types.Time, nullable=False)

    #: Reserved field. Information derived from file header.
    plx_fast_read = Column(types.Integer, nullable=False)

    #: Sampling rate for waveforms (may differ from :data:`ADFrequency`). Information derived from file header.
    #:
    #: .. seealso:: Attributes :attr:`ADFrequency`, :attr:`ad_frequency`, :attr:`waveform_freq`
    plx_waveform_freq = Column(types.Integer, nullable=False)

    #: Duration of recording (in number of timestamps). Information derived from file header.
    #:
    #: .. seealso:: Attributes :attr:`duration`, :attr:`duration_ts`
    plx_last_timestamp = Column(types.Integer, nullable=False)

    #: Trodalness (type of electrode) of recording. Information derived from file header.
    plx_trodalness = Column(types.Enum(RecordingTrodalness), nullable=False)

    #: Trodalness (type of electrode) of data representation? Information derived from file header.
    plx_data_trodalness = Column(types.Enum(RecordingTrodalness), nullable=False)

    #: Bits per spike waveform sample (usually 16). Information derived from file header.
    plx_bits_per_spike_sample = Column(types.Integer, nullable=False)

    #: Bits per slow waveform sample (usually 16). Information derived from file header.
    plx_bits_per_slow_sample = Column(types.Integer, nullable=False)

    #: Zero-to-peak voltage (in mV) for spike waveform values. Information derived from file header.
    #:
    #: .. seealso:: Attributes :attr:`SlowMaxMagnitudeMV`, :attr:`slow_max_magnitude`, :attr:`spike_max_magnitude`
    plx_spike_max_magnitude_mv = Column(types.Integer, nullable=False)

    #: Zero-to-peak voltage (in mV) for slow saveform values. Information derived from file header.
    #:
    #: .. seealso:: Attributes :attr:`SpikeMaxMagnitudeMV`, :attr:`slow_max_magnitude`, :attr:`spike_max_magnitude`
    plx_slow_max_magnitude_mv = Column(types.Integer, nullable=False)

    #: Pre-amplification gain for spike waveforms. Information derived from file header.
    plx_spike_preamp_gain = Column(types.Integer, nullable=False)

    #: Number of trials (repetitions) per condition (stimulus variation).
    # .. todo:: Should be a mapped column (to session.trials_per_condition), not a hard-coded constant.
    trials_per_condition = 10  # type: int

    # This needs to be declared here to avoid problems with the v2.sorting.ifs interfaces requiring all methods to be
    # implemented in the v2.db.model.sorting.core.Sorting entity-class.
    # all_sortings = v2.db.sqlite('Sorting', back_populates='recording')

    __table_args__ = (
        CheckConstraint(or_(depth_left_um != None, depth_right_um != None)),
        CheckConstraint(plx_last_timestamp >= 0),
    )

    @hybrid_property
    def date_time(self):
        return dateutil.parser.parse(f"{self.plx_date}T{self.plx_time}")

    @date_time.expression
    def date_time(self):
        return self.plx_date + "T" + self.plx_time

    @staticmethod
    def test_file_id():
        """DEPRECATED"""
        return 151

    # .. todo:: Review methods below, which were adapted from old DatasetPlxFile class
    # @staticmethod
    # def denormalized_spike_waveform(header, spikeheaders, channel, samples):
    #     gain = spikeheaders[channel]['Gain']
    #     maxmag = header['SpikeMaxMagnitudeMV']
    #     bitrange = 2 ** header['BitsPerSpikeSample']
    #     preampgain = header['SpikePreAmpGain']
    #
    #     if header['Version'] < 105:
    #         preampgain = 1000
    #     if header['Version'] < 103:
    #         maxmag = 3000
    #         bitrange = 4096
    #
    #     return samples.astype(numpy.float) * maxmag / (0.5 * bitrange * gain * preampgain)
    #
    # @staticmethod
    # def denormalized_slow_waveform(header, slowheaders, signame, samples):
    #     gain = slowheaders[signame]['Gain']
    #     maxmag = header['SlowMaxMagnitudeMV']
    #     bitrange = 2 ** header['BitsPerSlowSample']
    #     preampgain = slowheaders[signame]['PreAmpGain']
    #
    #     if header['Version'] < 103:
    #         maxmag = 5000
    #         bitrange = 4096
    #     if header['Version'] < 102:
    #         preampgain = 1000
    #
    #     return samples.astype(numpy.float) * maxmag / (0.5 * bitrange * gain * preampgain)

    @property
    def ad_frequency(self):
        """Unit-aware version of the :attr:`ADFrequency` property.

        :rtype: v2_dataset.units.Quantity (of time frequency)

        See also
        --------
        waveform_freq
        """
        return self.plx_ad_frequency * units.hertz

    @property
    def channels(self):
        """Number of electrodes recorded in this file.

        :rtype: int
        """
        return self.session.electrodes_left + self.session.electrodes_right

    @property
    def condition_type(self):
        """Returns the enumeration class that represents the stimulus variations in this experiments. For further
        information, refer to the :mod:`v2.db.parsing` module."""
        return self.stimulus.conditions_type

    @property
    def conditions(self):
        """Number of different conditions stimulus variations present in this file."""
        return len(self.condition_type.stimulus_variations())

    @property
    def date(self):
        """types.Date and time of recording start.

        :rtype: datetime.datetime

        See also
        --------
        :attr:`types.Date`, :attr:`Time`
        """
        return datetime.datetime.combine(date=self.plx_date, time=self.plx_time)

    @property
    def depth_left(self):
        """Unit aware version of :attr:`depth_left_um`.

        :rtype: v2_dataset.units.Quantity (of space)
        """
        return self.depth_left_um * units.micrometer

    @property
    def depth_right(self):
        """Unit aware version of :attr:`depth_right_um`.

        :rtype: v2_dataset.units.Quantity (of space)
        """
        return self.depth_right_um * units.micrometer

    @property
    def duration_ts(self):
        """Duration of this recording, in timestamps. Alias for :attr:`LastTimestamp`.

        :rtype: int

        See also
        --------
        LastTimestamp, duration
        """
        return self.plx_last_timestamp

    @property
    def slow_max_magnitude(self):
        """Unit-aware version of the :attr:`SlowMaxMagnitudeMV` property.

        :rtype: v2_dataset.units.Quantity (of electrical potential)
        """
        return self.plx_slow_max_magnitude_mv * units.millivolt

    @property
    def spike_max_magnitude(self):
        """Unit-aware version of the :attr:`SpikeMaxMagnitudeMV` property.

        :rtype: v2_dataset.units.Quantity (of electrical potential)
        """
        return self.plx_spike_max_magnitude_mv * units.millivolt

    @property
    def waveform_freq(self):
        """Unit-aware version of the :attr:`WaveformFreq` property.

        :rtype: v2_dataset.units.Quantity (of time frequency)
        """
        return self.plx_waveform_freq * units.hertz

    @property
    def mea_depth(self):
        """Left- and right-hemisphere depth of the multi-electrode array (MEA) used in this recording.

        :rtype: MeaDepth
        """
        return MeaDepth(
            left=self.depth_left_um and self.depth_left_um * units.micrometer,
            right=self.depth_right_um and self.depth_right_um * units.micrometer,
        )

    @property
    def mea_layout(self):
        """Layout of the multi-electrode array (MEA) used in this recording.

        .. todo:: This property actually belongs in the :class:`RecordingSession` class.

        :rtype: MeaLayout
        """
        return MeaLayout(
            rows=self.session.electrode_rows, cols=self.session.electrode_cols
        )

    @property
    def path(self):
        """Path to the corresponding *PLX* file in the annex.

        :rtype: pathlib.Path
        """
        path = config.dataset_dir / f"files/recording/id/{self.id}/file.plx"
        return path

    @property
    def sampling_rate(self):
        return self.ad_frequency

    @property
    def subject(self):
        """Test subject. Alias to :attr:`session.subject <RecordingSession.subject>`."""
        return self.session.subject

    @property
    def waveform_sampling(self):
        """Information about waveform sampling characteristics in all spike channels.

        :rtype: v2.db.model.WaveformSamplingProperties
        """
        return WaveformSamplingProperties(
            samples=self.plx_num_points_wave,
            samples_pre_thr=self.plx_num_points_pre_thr,
            sampling_rate=self.plx_waveform_freq * units.hertz,
        )

    def duration_of(self, condition, session=None):
        """Duration of a certain condition (stimulus variation).
        """
        if session is None:
            session = self.scoped_session
        max_duration_ts = max(
            session.query(Trial.duration_ts)
            .filter(Recording.id == self.id, Trial.condition_code == condition)
            .all_scalars()
        )
        max_duration = max_duration_ts / self.waveform_freq
        return max_duration

    def firing_rate(
        self,
        condition,
        channel,
        kernel_sigma=50 * units.ms,
        sampling_rate=100 * units.hertz,
        hist_extend="border",
    ):
        """Compute firing rates for a certain spike channel, by averaging over all trials of a specific condition.

        .. todo:: This should perhaps be moved to :class:`SpikeChannel`.
        """
        return signal.firing_rate(
            spikes=signal.spike_hist(
                ts=self.spike_times(condition, channel),
                rate=sampling_rate,
                duration=self.duration_of(condition),
            ),
            kernel=kernels.gaussian(sigma=kernel_sigma, rate=sampling_rate),
            rate=sampling_rate,
            extend=hist_extend,
        )

    def json(self):
        """Convert to JSON string.

        .. todo:: Deprecated. Use marshmallow and sqlalchemy-marshmallow for serialization instead.

        :rtype: str
        """
        return json.dumps(
            {
                "channels": self.channels,
                "conditions": self.conditions,
                "mea_layout": {
                    "rows": self.mea_layout.rows,
                    "cols": self.mea_layout.cols,
                },
                "date": self.date.strftime("%Y-%m-%dT%H:%M:%S-03:00"),
                "mea_depth": {
                    "left": self.mea_depth.left and self.mea_depth.left.m,
                    "right": self.mea_depth.right and self.mea_depth.right.m,
                },
                "duration": self.duration.to("sec").m,
                "sampling_rate": self.ad_frequency.to("hertz").m,
                "original_paths": [
                    {"directory": path.directory, "filename": path.filename}
                    for path in self.paths
                ],
                "stimulus": self.stimulus,
                "subject": self.subject.name,
            }
        )

    def raw_data(self, condition, channel):
        """
        .. todo:: DEPRECATED. Trial parsing has been implemented, so this is not needed anymore. However, this method is
                  still being used.
        """
        path = [
            part
            for part in self.parts
            if part.channel == channel and part.condition == condition
        ][0].path
        with open(path) as file:
            return json.load(file)

    def spike_times(self, condition, channel):
        """
        .. todo:: DEPRECATED. This information can be accessed from the :attr:`spike_channels` relationship.
        """
        return [
            numpy.array(trial["timestamps"]) * units.ms
            for trial in self.raw_data(condition, channel)["trials"]
        ]


class RecordingPath(Model):
    """Filesystem paths originally associated with PLX files.
    """

    #: Sequence of /-separated directories that locate the file, relative to the dataset's root.
    directory = Column(types.String, nullable=False, primary_key=True)

    #: Last portion of file path (base name), which ends in a ``.plx`` extension.
    filename = Column(types.String, nullable=False, primary_key=True)

    #: The PLX file this path refers to.
    #:
    #: .. seealso:: Relationship :attr:`recording`
    recording_id = Column(types.Integer, StrictForeignKey(Recording.id), nullable=False)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.directory!r}, {self.filename!r}, {self.recording_id!r})"

    def as_path(self):
        """Join :attr:`directory` and :attr:`filename` components.

        :rtype: pathlib.Path
        """
        return pathlib.Path(self.directory).joinpath(self.filename)


class SpikeChannel(
    Model, mixins.PrimaryKey, SpikeTrainMixin, TimeRangeMixin, TrialSliceMixin
):
    """Access to spike timestamps and waveform clips originating from a specific electrode in a :class:`PlxFile`.

    Notes
    -----
    Some of the ``waveform_*`` properties are actually shortcuts for properties in ``recording.sampling``, e.g.

        >>> spk_chan.waveform_duration.to('us')
        units.Quantity(775.0, 'microsecond')
        >>> spk_chan.recording.sampling.duration.to('us')
        units.Quantity(775.0, 'microsecond')

    hence they should give the same values for all spike channels associated to a common :class:`PlxFile` object. Check
    the documentation on the :class:`lib.WaveformSamplingProperties` if you need more information about what sampling
    properties are available.
    """

    #: Points to the :class:`PlxFile` instance to which this spike channel belongs.
    #:
    #: .. seealso:: Relationship :attr:`recording`
    recording_id = Column(types.Integer, StrictForeignKey(Recording.id), nullable=False)

    electrode_id = Column(types.Integer, StrictForeignKey(Electrode.id))

    #: Actual gain divided by `recording.SpikePreAmpGain`.
    gain = Column(types.Integer, nullable=False)

    #: Spike detection threshold in A/D values.
    threshold = Column(types.Integer, nullable=False)

    #: Total number of spikes detected in this channel.
    n_spikes = Column(types.Integer, nullable=False)

    #: Spike timestamps (in clock ticks).
    timestamps = Column(types.NumpyArray, nullable=False)

    #: Waveform A/D samples.
    waveforms = Column(types.NumpyArray, nullable=False)

    electrode = relationship(Electrode)
    channel = association_proxy("electrode", "channel")

    __table_args__ = (
        UniqueConstraint(recording_id, electrode_id),
        CheckConstraint(n_spikes >= 0),
    )

    @property
    def duration_ts(self) -> int:
        return self.recording.duration_ts

    @property
    def sampling_rate(self):
        return self.waveform_sampling_rate

    @property
    def waveform_duration(self):
        """Elapsed time between first and last samples in waveform clips.

        :rtype: v2_dataset.units.Quantity
        """
        return self.recording.waveform_sampling.duration

    @property
    def waveform_samples(self):
        """Total number of samples in waveform clips.

        :rtype: int
        """
        return self.recording.waveform_sampling.samples

    @property
    def waveform_samples_post_thr(self):
        """Number of samples after threshold (including time of threshold) in waveform clips.

        :rtype: int
        """
        return self.recording.waveform_sampling.samples_post_thr

    @property
    def waveform_samples_pre_thr(self):
        """Number of samples in waveform clips prior to threshold crossing.

        :rtype: int
        """
        return self.recording.waveform_sampling.sample_pre_thr

    @property
    def waveform_sample_interval(self):
        """Time interval between consecutive samples in waveform clips.

        :rtype: v2_dataset.units.Quantity
        """
        return self.recording.waveform_sampling.sample_interval

    @property
    def waveform_sampling_rate(self):
        """Rate at which waveform samples are taken.

        :rtype: v2_dataset.units.Quantity
        """
        return self.recording.waveform_sampling.sampling_rate

    @property
    def waveform_threshold_time(self):
        """The time instant, relative to waveform clips' start instants, at which waveform threshold occurs.

        :rtype: v2_dataset.units.Quantity
        """
        return self.recording.waveform_sampling.threshold_time


class Trial(Model, TimeRangeMixin):
    #: Primary key.
    id = Column(types.Integer, primary_key=True)

    #: Points to the :class:`PlxFile` instance during which this trial took place.
    recording_id = Column(types.Integer, StrictForeignKey(Recording.id), nullable=False)

    #: Points to the trial that comes immediately after this one in the corresponding recording.
    next_id = Column(types.Integer, StrictForeignKey(id))

    #: The *condition code* indicates which stimulus variation took place during this trial.
    condition_code = Column(types.Integer, nullable=False)

    #: Timestamp of trial start.
    start_ts = Column(types.Integer, nullable=False)

    #: Trial duration, in timestamps.
    duration_ts = Column(types.Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(recording_id, start_ts),
        CheckConstraint(start_ts >= 0),
        CheckConstraint(duration_ts >= 0),
    )

    @property
    def condition(self):
        """A rich enumeration value that describes the stimulus variation (a.k.a condition) that was presented during
        this trial.

        Returns
        -------
        A values from one of the enumerated types from :mod:`v2.db.parsing`. The actual enumerated type depends on
        the type of stimulus.
        """
        stimulus = self.recording.stimulus
        try:
            return self.recording.stimulus.conditions_type(self.condition_code)
        except KeyError:
            raise RuntimeError(f"Unimplemented stimulus value {stimulus!r}")

    @property
    def sampling_rate(self):
        return self.recording.sampling_rate


# TODO: Not sure if this works.
# Recording.repeated_by = relationship(Recording, backref='repeats', foreign_keys=[Recording.repeated_by_id])
# Recording.sorting_of = relationship(Recording, backref='sorted_by', foreign_keys=[Recording.sorting_of_id])

RecordingSession.mea_left = relationship(
    MEA,
    backref=backref("sessions_at_left"),
    remote_side=[MEA.id],
    foreign_keys=[RecordingSession.mea_left_id],
)
RecordingSession.mea_right = relationship(
    MEA,
    backref=backref("sessions_at_right"),
    remote_side=[MEA.id],
    foreign_keys=[RecordingSession.mea_right_id],
)

Trial.next = relationship(
    Trial, backref=backref("previous", uselist=False), remote_side=[Trial.id]
)
Trial.next.__doc__ = """\
Retrieves the trial-entity that immediately succeeds this one, if any. There is also a corresponding attribute
:attr:`previous` that goes in the opposite direction.
"""

Model.relate_1_to_n(
    Recording,
    SpikeChannel,
    "spike_channels",
    "recording",
    side1_kwargs={"order_by": SpikeChannel.electrode_id},
)
Model.relate_1_to_n(
    Recording, Trial, "trials", "recording", side1_kwargs={"order_by": Trial.start_ts}
)
Model.relate_1_to_n(Recording, RecordingPath, "paths", "recording")

Model.relate_1_to_n(
    RecordingSession,
    Electrode,
    "electrodes",
    "session",
    side1_kwargs={"order_by": Electrode.channel},
)
Model.relate_1_to_n(RecordingSession, Recording, "recordings", "session")
