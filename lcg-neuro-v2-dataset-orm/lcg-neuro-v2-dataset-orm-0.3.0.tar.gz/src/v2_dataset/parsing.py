r"""Support to the interpretation of experimental data.

In this dataset, each recording is represented by a :class:`v2.db.model.Recording` entity-object in the database,
obtained by parsing a corresponding :mod:`PLX file <plx.parsing>` with an :class:`plx.AbstractPlxFile`
instance. A recording may be divided on multiple non-overlapping *trials*, each trial consisting in the presentation of
a stimulus variation for a limited amount of time. These stimulus variations are referred to as *conditions*, and the
start/end of conditions is recorded in the event data blocks of :mod:`PLX files <plx.parsing>` using a binary
encoding based on the :mod:`event channels <plx.parsing.EventHeader>` of the data blocks.

Condition codes are represented by enumeration types particular to each stimulus type (like :class:`MovingBarConditions`
for moving bar stimuli, for example). Parsing an array of events, as obtained from the
:meth:`plx.AbstractPlxFile.event_data` method, may be achieved with the :func:`parse_trials` function. For more
information on how conditions are encoded in *PLX* files, read on the section below.

Condition encoding
------------------

Some :mod:`event channels <plx.parsing.EventHeader>` have a special meaning, while others may be used by a client
program that generates stimuli to record information about it. For example, all *PLX* files record single events in

* Channel 258 (or :attr:`CommonConditions.PLX_START`) to signal start/resume of a recording, and
* Channel 259 (or :attr:`CommonConditions.PLX_STOP`) to signal stop/pause of it.

Meanwhile, the ``MB_colours_Eizo`` Matlab program that generates *moving bar* stimuli, records events in some of the
user channels 1-8 at a specific timestamp as a way to signal the start/end of one of 8 different conditions (8 different
directions of the moving bar). Given a timestamp :math:`t`, for which there exists at least one recorded event in
channels 1-8, the *condition code* is obtained as

.. math::

    c(t) = \sum_{i=1}^{8} 2^{8-i} E_i(t)

where :math:`E_i(t)` represents whether there exists a recorded event for channel :math:`i` at timestamp :math:`t`. The
special codes 255 (:attr:`CommonConditions.PROTOCOL_START`) and 254 (:attr:`CommonConditions.PROTOCOL_END`) represent,
respectively, the start and end of the *experimental protocol* (unlike the builtin values 258 and 259, previously
described), and codes 1-8 represent the 8 different directions of the moving bar. The diagram below illustrates a
recording in which the sequence of conditions :math:`{c_i} = {4, 3, 1, 2, 7, 5}`, starting at times :math:`{t_i} = {t_1,
t_2, t_3, t_4, t_5, t_6}`, are presented to the test subject (the *X* denotes that an event was recorded for the channel
indicated by its row, on the timestamp indicated by its column):

+---------+--------------------------------------------------+
|         | Timestamps :math:`t_i`, where :math:`i` is       |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
| Channel |       |  0  | 1 | 2 | 3 | 4 | 5 | 6 |  7  |   8  |
+=========+=======+=====+===+===+===+===+===+===+=====+======+
|1        |       |  X  |   |   |   |   |   |   |  X  |      |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
|2        |       |  X  |   |   |   |   |   |   |  X  |      |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
|3        |       |  X  |   |   |   |   |   |   |  X  |      |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
|4        |       |  X  |   |   |   |   |   |   |  X  |      |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
|5        |       |  X  |   |   |   |   |   |   |  X  |      |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
|6        |       |  X  | X |   |   |   | X | X |  X  |      |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
|7        |       |  X  |   | X |   | X | X |   |  X  |      |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
|8        |       |  X  |   | X | X |   | X | X |     |      |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
|258      |   X   |     |   |   |   |   |   |   |     |      |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
|259      |       |     |   |   |   |   |   |   |     |   X  |
+---------+-------+-----+---+---+---+---+---+---+-----+------+
| Cond.   | Start | 255 | 4 | 3 | 1 | 2 | 7 | 5 | 254 | Stop |
+---------+-------+-----+---+---+---+---+---+---+-----+------+

In this example, the start and end of recording, as signaled by the recording equipment via channels 258 and 259,
correspond to the timestamps :math:`t=0` and :math:`t=t_8`, whereas the end of the experimental protocol is delimited
by the condition codes 255 (at :math:`t=t_0`) and 254 (at :math:`t=t_7`). The *ordinary* condition codes, corresponding
to actual stimulus variations, fall in between, encoded by the condition bits that are set by individual events. In this
case, the number of *X* marks in the table corresponds to the number of event data blocks that would have been recorded
in the corresponding hypothetical *PLX* file, that is 27.
"""

import math
import numpy
import pandas
import sys
import plx.export
import tempfile

from sqlalchemy.orm.exc import NoResultFound
from v2_dataset import model


def _create_or_update(
    session,
    filters,
    entity_type,
    entity_data=None,
    create_n_sides=None,
    create_1_sides=None,
):
    """Shortcut for updating an existing object with given data, if it exists, or creating it from scratch, if it
    doesn't. If the object is created, it is possible to adjust its relationships by informing them.

    Example
    -------
    The first usage on the :func:`parse_trials` function, below in this module, is

    .. code:: python

        _create_or_update(
            session=session,
            entity_type=db.model.SpikeChannel,
            filters=[
                db.model.SpikeChannel.recording_id == recording.id,
                db.model.SpikeChannel.channel == channel,
            ],
            create_n_sides=[recording.spike_channels],
            entity_data=spike_channel_dicts[channel],
        )

    Which is a actually a replacement for

    .. code::python

        instance = session.query(db.model.SpikeChannel).filter([
            db.model.SpikeChannel.recording_id == recording.id,
            db.model.SpikeChannel.channel == channel,
        ]).one_or_none()

        if instance:  # Updating the object, because it exists already in the given session.
            for key, val in spike_channel_dicts[channel].items():
                setattr(instance, key, val)
        else:         # Creating a new object and inserting it on the remote side of relationships
            instance = db.model.SpikeChannel(**spike_channel_dicts[channel])
            recording.spike_channels.append(instance)

    :param session: Result of a query that should produce the updated object, if it exists.
    :param filters: The list of filtering expressions passed to :meth:`sqlalchemy.orm.query.Query.filter`.
    :param entity_type: The entity type that will be created/updated.
    :param entity_data: Dictionary of attributes to create/update.
    :param create_n_sides: List of relationship objects (for 1-to-N relationships), in which the present entity is
        on the 1-side, to which the entity should be appended if it is created.
    :param create_1_sides: List of relationship name-target pairs (for 1-to-N relationships), in which the present
        entity is on the N side, that should be updated in order to point to the specified targets.
    :return:
    """
    entity_data = entity_data or {}
    create_n_sides = create_n_sides or []
    create_1_sides = create_1_sides or []

    instance = session.query(entity_type).filter(*filters).one_or_none()
    if instance:
        for key, val in entity_data.items():
            setattr(instance, key, val)
    else:
        instance = entity_type(**entity_data)
        for rel in create_n_sides:
            rel.append(instance)
        for rel, target in create_1_sides:
            setattr(instance, rel, target)
    return instance


def _get_plx_file(recording):
    export_dir = tempfile.TemporaryDirectory()
    plx_file = plx.PlxFile(recording.path, export_base_dir=export_dir.name)
    return plx_file


def _parse_trials(event_data, stimulus):
    """Parse *PLX* event data into trials.

    Parameters
    ----------
    event_data: numpy.ndarray
        An array of event records with datatype :attr:`plx.export.ExportedEvent.dtype` (may be obtained from the
        :meth:`plx.AbstractPlxFile.event_data`` method).

    stimulus: v2_dataset.model.Stimulus
        Type of stimulus.

    Returns
    -------
    trials: numpy.array
        A record array where each entry describes a trial. This array contains the following fields:

        condition:
            :class:`object` - the condition code for this trial. The actual type of the objects will be one of the
            enumeration types defined in this module, such as :class:`MovingBarConditions`. More precisely, it will be
            the result of :code:`stimulus.conditions_type`.

        start:
            :class:`numpy.uint64` - the timestamp where this trial starts.

        duration:
            :class:`numpy.uint64` - the duration of this trial, in timestamp units.
    """
    # Convert event data to pandas DataFrame.
    events = pandas.DataFrame(event_data)

    # Evaluate event codes:
    # * Events from channels 1-8 get a partial event code corresponding to a power of 2
    # * For other events, set the condition code to the value of the channel
    condition_channels = events["channel"] <= 8
    events.loc[~condition_channels, "condition"] = events.loc[
        ~condition_channels, "channel"
    ]
    events.loc[condition_channels, "condition"] = numpy.array(
        events[condition_channels].eval("2**(8-channel)")
    )

    # Trials obtained by grouping the events on the 'timestamp' field. Final condition codes are the sum of partial
    # condition codes (disjoint powers of two) in the same timestamp.
    trials = pandas.DataFrame(
        {
            "condition": numpy.array(
                events.groupby("timestamp")["condition"].sum()
            ).astype(object),
            "start": events["timestamp"].unique(),
            "duration": numpy.uint64(0),
        }
    )

    # Setting the 'duration' field in the 'trials' DataFrame.
    first, last = trials.index[0 :: len(trials) - 1]
    trials.loc[first : last - 1, "duration"] = numpy.array(
        trials.loc[first + 1 : last, "start"]
    ) - numpy.array(trials.loc[first : last - 1, "start"])

    #: Fix condition codes into correct enumeration type (MovingBarConditions, in this case).
    for i, t in trials.iterrows():
        trials.loc[i, "condition"] = stimulus.conditions_type(
            trials.loc[i, "condition"]
        )

    return trials.to_records(index=False)


def parse_spike_channels(recording, session, plx_file=None):
    """Parse spike channel data from a dataset recording's (:class:`v2_dataset.model.Recording`) associated *PLX*
    file (:class:`plx.AbstractPlxFile`), creating corresponding :mod:`v2_dataset.model` entities and binding them to
    the recording object. If a :class:`sqlalchemy.orm.session.Session` is provided, the given recording and its newly
    associated objects will be added to the session (:meth:`v2_dataset.db.Session.add <sqlalchemy.orm.session.Session.add>`)
    **but not committed**. If a :class:`plx.AbstractPlxFile` instance corresponding to the recording is not given, it
    will be searched for in the dataset directory (:attr:`v2_dataset.db.config.dataset_dir <v2_dataset.db.config.Config.dataset_dir>`).

    Spike channel data will mainly result in the creation of :class:`v2_dataset.model.SpikeChannel` entities, but other
    entities may be created to represent embedded spike sorting, if the spike channels in the PLX file discriminate
    units in recorded spike data-blocks (:class:`plx.parsing.DataBlockHeader`). The extra entities that may be
    created are:

    * One :class:`v2_dataset.model.EmbeddedSorting` instance to represent the existence of embedded sorting,
    * One :class:`v2_dataset.model.SortedChannel` for each :class:`v2_dataset.model.SpikeChannel` created, and
    * As many :class:`v2_dataset.model.SortedUnit` instances as needed to represent the individual units of each
      :class:`v2_dataset.model.SortedChannel` object (none may be created, if there are no spikes for this channel, as noted
      below).
      
    Parameters
    ----------
    recording: v2_dataset.model.Recording recording
        The source recording.
        
    session: sqlalchemy.orm.session.Session
        A :class:`database <v2_dataset.db.Database>` session to attach (add/update) new entities created. It must be
        **the same session** from where the recording came.
        
    plx_file: plx.AbstractPlxFile plx_file
        An optional PLX file object corresponding to the given recording. If not provided, the function attempts to
        retrieve it from the configured dataset directory (:attr:`v2_dataset.config.dataset_dir`).

    Warnings
    --------
    Existing entities associated to the recording are overwritten!

    Notes
    -----
    The number of channels in a *PLX* file is usually a power of two. It may be the case that a spike channel was
    active during recording --- *i.e.*, there is a :class:`plx.parsing.SpikeHeader` for the channel in
    the file's main header (:class:`plx.parsing.Header`) --- but there were no electrodes associated to it,
    or no spikes recorded whatsoever. For this reason, the :attr:`plx.parsing.Header.num_dsp_channels` header
    field (which corresponds to the number of spike channel headers declared in the file) is not a reliable way of
    determining the actual number of electrodes used. This function will assume the actual number of channels to be
    *the least power of two greater or equal than the largest spike channel number detected*. This function will
    create as many :class:`v2_dataset.model.SpikeChannel` entities as this number, **even if they contain no spikes**
    (see :attr:`v2_dataset.model.SpikeChannel.n_spikes`). Likewise, if there is embedded sorting information, a
    :class:`v2_dataset.model.SortedChannel` instance will be created for each spike channel, but associated
    :class:`v2_dataset.model.SortedUnit` objects will not be created for a channel without spikes.
        
    Raises
    ------
    sqlalchemy.exc.InvalidRequestError
        If the given database session is different from the one to which the recording belongs.
    """
    plx_file = plx_file or _get_plx_file(recording)

    # Gather spike channel entity properties for exported channels with actual data and compute their unit counts.
    n_channels = 0
    max_spike_channel_units = {}
    spike_channel_dicts = {}
    for i in range(len(plx_file.spike_headers)):
        channel = i + 1
        spike_header = plx_file.spike_channel(channel).header
        spike_data = plx_file.spike_channel(channel).data
        spike_channel_dicts[channel] = dict(
            gain=spike_header["Gain"],
            threshold=spike_header["Threshold"],
            n_spikes=len(spike_data),
            timestamps=spike_data["timestamp"],
            waveforms=spike_data["waveform"],
        )

        electrode_query = session.query(model.Electrode).filter_by(
            session_id=recording.session_id, channel=spike_header["Channel"]
        )

        if len(spike_data) > 0:
            try:
                spike_channel_dicts[channel]["electrode"] = electrode_query.one()
            except NoResultFound:
                sys.stderr.write(
                    f"No electrode found for channel {channel} (session ID {recording.session_id}), which contains "
                    "data! This is likely a dataset curation error."
                )
                sys.stderr.flush()
                sys.exit(1)
            n_channels = 2 ** math.ceil(math.log(channel, 2))
            max_spike_channel_units[channel] = numpy.max(spike_data["unit"])
        else:
            spike_channel_dicts[channel]["electrode"] = electrode_query.one_or_none()

    # Create/update spike channel entities using the gathered information.
    for channel in range(1, n_channels + 1):
        _create_or_update(
            session=session,
            entity_type=model.SpikeChannel,
            filters=[
                model.SpikeChannel.recording_id == recording.id,
                model.SpikeChannel.channel == channel,
            ],
            create_n_sides=[recording.spike_channels],
            entity_data=spike_channel_dicts[channel],
        )

    # Create entities to represent embedded sorting information, if any.
    if max(max_spike_channel_units.values()) > 1:
        embedded_sorting = _create_or_update(
            session=session,
            entity_type=model.EmbeddedSorting,
            filters=[model.EmbeddedSorting.recording_id == recording.id],
            create_1_sides=[("recording", recording)],
            entity_data={},
        )

        # Create one sorted channel entity (with as many sorted units as required) per spike channel.
        for spike_channel in recording.spike_channels:
            n_units = max_spike_channel_units.get(spike_channel.channel, 0)

            sorted_channel = _create_or_update(
                session=session,
                entity_type=model.SortedChannel,
                filters=[
                    model.SortedChannel.sorting_id == embedded_sorting.id,
                    model.SortedChannel.spike_channel_id == spike_channel.id,
                ],
                create_n_sides=[embedded_sorting.sorted_channels],
                create_1_sides=[
                    ("sorting", embedded_sorting),
                    ("spike_channel", spike_channel),
                ],
                entity_data={
                    "spike_labels": plx_file.spike_channel(spike_channel.channel).data[
                        "unit"
                    ]
                },
            )

            for unit in range(1, n_units + 1):
                unit_mask = (
                    plx_file.spike_channel(spike_channel.channel).data["unit"] == unit
                )
                unit_n_spikes = int(numpy.sum(unit_mask))
                unit_data = dict(label=unit, n_spikes=unit_n_spikes)

                _create_or_update(
                    session=session,
                    entity_type=model.SortedUnit,
                    filters=[
                        model.SortedUnit.sorted_channel_id == sorted_channel.id,
                        model.SortedUnit.label == unit,
                    ],
                    create_n_sides=[sorted_channel.sorted_units],
                    entity_data=unit_data,
                )


def parse_trials(recording, session, plx_file=None):
    """Parse experiment trials from a dataset recording's (:class:`v2_dataset.model.Recording`) associated *PLX* file
    (:class:`plx.AbstractPlxFile`), creating corresponding :mod:`v2_dataset.model.Trial` entities and binding them to the
    recording object. If a :class:`sqlalchemy.orm.session.Session` is provided, the given recording and its newly
    associated objects will be added to the session (:meth:`v2_dataset.db.Session.add <sqlalchemy.orm.session.Session.add>`)
    **but not committed**. If a :class:`plx.AbstractPlxFile` instance corresponding to the recording is not given, it
    will be searched for in the dataset directory (:attr:`v2_dataset.db.config.dataset_dir <v2_dataset.db.config.Config.dataset_dir>`).
    
    Parameters
    ----------
    recording: v2_dataset.model.Recording recording:
        The source recording.
        
    session: sqlalchemy.orm.session.Session
        A :class:`database <v2_dataset.db.Database>` session to attach (add/update) new entities created. It must be
        **the same session** from where the recording came.

    plx_file: plx.AbstractPlxFile
        An optional PLX file object corresponding to the given recording. If not provided, the function attempts to
        retrieve it from the configured dataset directory (:attr:`v2_dataset.config.dataset_dir`).

    Warnings
    --------
    Existing entities associated to the recording are overwritten!

    Notes
    -----
    The set of currently supported stimulus (:attr:`v2_dataset.model.Recording.stimulus`) types is given by the
    :data:`conditions_map` dictionary.
    """
    plx_file = plx_file or _get_plx_file(recording)
    trial_records = _parse_trials(plx_file.event_data(), recording.stimulus)

    # For each parsed trial, create the corresponding Trial-entity and bind it to the recording.
    prev_trial = None
    for trial_rec in trial_records:
        trial_data = dict(
            condition_code=trial_rec["condition"].value,
            start_ts=int(trial_rec["start"]),
            duration_ts=int(trial_rec["duration"]),
        )

        trial = _create_or_update(
            session=session,
            entity_type=model.Trial,
            filters=[
                model.Trial.recording_id == recording.id,
                model.Trial.start_ts == trial_data["start_ts"],
            ],
            create_n_sides=[recording.trials],
            entity_data=trial_data,
        )

        if prev_trial is not None:
            prev_trial.next = trial
        prev_trial = trial
