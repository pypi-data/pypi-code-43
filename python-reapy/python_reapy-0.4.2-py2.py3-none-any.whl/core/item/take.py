import reapy
from reapy import reascript_api as RPR
from reapy.core import ReapyObject


class Take(ReapyObject):

    _class_name = "Take"

    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return self.id == other.id

    @property
    def _args(self):
        return self.id,

    def add_audio_accessor(self):
        """
        Create audio accessor and return it.

        Returns
        -------
        audio_accessor : AudioAccessor
            Audio accessor on take.
        """
        audio_accessor_id = RPR.CreateTakeAudioAccessor(self.id)
        audio_accessor = reapy.AudioAccessor(audio_accessor_id)
        return audio_accessor

    def add_fx(self, name, even_if_exists=True):
        """
        Add FX to track and return it.

        Parameters
        ----------
        name : str
            FX name.
        even_if_exists : bool, optional
            Whether the FX should be added even if there already is an
            instance of the same FX on the track (default=True).

        Returns
        -------
        fx : FX
            New FX on take (or previously existing instance of FX if
            even_if_exists=False).

        Raises
        ------
        ValueError
            If there is no FX with the specified name.
        """
        index = RPR.TakeFX_AddByName(
            self.id, name, 1 - 2*even_if_exists
        )
        if index == -1:
            raise ValueError("Can't find FX named {}".format(name))
        fx = reapy.FX(self, index)
        return fx

    @reapy.inside_reaper()
    def add_note(
        self, start, end, pitch, velocity=100, channel=0, selected=False,
        muted=False, unit="seconds", sort=True
    ):
        """
        Add MIDI note to take.

        Parameters
        ----------
        start : float
            Note start. Unit depends on ``unit``.
        end : float
            Note end. Unit depends on ``unit``.
        pitch : int
            Note pitch between 0 and 127.
        velocity : int, optional
            Note velocity between 0 and 127 (default=100).
        channel : int, optional
            MIDI channel between 0 and 15.
        selected : bool, optional
            Whether to select new note (default=False).
        muted : bool
            Whether to mute new note (default=False).
        unit : {"seconds", "ppq", "beats"}, optional
            Time unit for ``start`` and ``end`` (default="seconds").
            ``"ppq"`` refers to MIDI ticks.
        sort : bool, optional
            Whether to resort notes after creating new note
            (default=True). If False, then the new note will be
            ``take.notes[-1]``. Otherwise it will be at its place in
            the time-sorted list ``take.notes``. Set to False for
            improved efficiency when adding several notes, then call
            ``Take.sort_events`` at the end.

        See also
        --------
        Take.sort_events
        """
        if unit == "beats":
            item_start_seconds = self.item.position
            take_start_beat = self.track.project.time_to_beats(item_start_seconds)
            start = self.beat_to_ppq(take_start_beat + start)
            end = self.beat_to_ppq(take_start_beat + end)
        elif unit == "seconds":
            item_start_seconds = self.item.position
            start = self.time_to_ppq(item_start_seconds + start)
            end = self.time_to_ppq(item_start_seconds + end)
        elif unit != 'ppq':
            raise ValueError('unit param should be one of seconds|beats|ppq')
        args = (
            self.id, selected, muted, start, end, channel, pitch, velocity,
            sort
        )
        RPR.MIDI_InsertNote(*args)

    def beat_to_ppq(self, beat):
        """
        Convert beat number (from project start) to MIDI ticks (of the take).

        Parameters
        ----------
        beat : float
            Beat time to convert in beats.

        Returns
        -------
        ppq : float
            Converted time in MIDI ticks of current take.

        See also
        --------
        Take.ppq_to_beat
        Take.time_to_ppq
        """
        ppq = RPR.MIDI_GetPPQPosFromProjQN(self.id, beat)
        return ppq

    @property
    def cc_events(self):
        """
        List of CC events on take.

        :type: CCList
        """
        return reapy.CCList(self)

    @property
    def envelopes(self):
        return reapy.EnvelopeList(self)

    @property
    def fxs(self):
        """
        FXs on take.

        :type: FXList
        """
        return reapy.FXList(self)

    def get_info_value(self, param_name):
        return RPR.GetMediaItemTakeInfo_Value(self.id, param_name)

    @reapy.inside_reaper()
    @property
    def is_active(self):
        """
        Whether take is active.

        :type: bool
        """
        return self == self.item.active_take

    @property
    def is_midi(self):
        """
        Whether take contains MIDI or audio.

        :type: bool
        """
        return bool(RPR.TakeIsMIDI(self.id))

    @property
    def item(self):
        """
        Parent item.

        :type: Item
        """
        return reapy.Item(RPR.GetMediaItemTake_Item(self.id))

    def make_active_take(self):
        """
        Make take active.
        """
        RPR.SetActiveTake(self.id)

    @property
    def n_cc(self):
        """
        Number of MIDI CC events in take (always 0 for audio takes).

        :type: int
        """
        return RPR.MIDI_CountEvts(self.id, 0, 0, 0)[3]

    @property
    def n_envelopes(self):
        """
        Number of envelopes on take.

        :type: int
        """
        return RPR.CountTakeEnvelopes(self.id)

    @property
    def n_fxs(self):
        """
        Number of FXs on take.

        :type: int
        """
        return RPR.TakeFX_GetCount(self.id)

    @property
    def n_notes(self):
        """
        Number of MIDI notes in take (always 0 for audio takes).

        :type: int
        """
        return RPR.MIDI_CountEvts(self.id, 0, 0, 0)[2]

    @property
    def n_text_sysex(self):
        """
        Number of MIDI text/sysex events in take (0 for audio takes).

        :type: int
        """
        return RPR.MIDI_CountEvts(self.id, 0, 0, 0)[4]

    @property
    def name(self):
        """
        Take name.

        :type: str
        """
        if self._is_defined:
            return RPR.GetTakeName(self.id)
        return ""

    @property
    def notes(self):
        """
        List of MIDI notes on take.

        Unless ``Take.add_note`` has been called with ``sort=False``,
        notes are time-sorted.

        :type: NoteList
        """
        return reapy.NoteList(self)

    def ppq_to_beat(self, ppq):
        """
        Convert time in MIDI ticks (from take's start) to beats (from project's start).

        Parameters
        ----------
        ppq : float
            Time to convert in MIDI ticks.

        Returns
        -------
        beat : float
            Converted time in beats.

        See also
        --------
        Take.beat_to_ppq
        Take.ppq_to_time
        """
        beat = RPR.MIDI_GetProjQNFromPPQPos(self.id, ppq)
        return beat

    def ppq_to_time(self, ppq):
        """
        Convert time in MIDI ticks to seconds.

        Parameters
        ----------
        ppq : float
            Time to convert in MIDI ticks.

        Returns
        -------
        time : float
            Converted time in seconds.

        See also
        --------
        Take.time_to_ppq
        """
        time = RPR.MIDI_GetProjTimeFromPPQPos(self.id, ppq)
        return time

    def select_all_midi_events(self, select=True):
        """
        Select or unselect all MIDI events.

        Parameters
        ----------
        select : bool
            Whether to select or unselect events.

        See also
        --------
        Take.unselect_all_midi_events
        """
        RPR.MIDI_SelectAll(self.id, select)

    def sort_events(self):
        """
        Sort MIDI events on take.

        This is only needed if ``Take.add_note`` was called with
        ``sort=False``.

        Examples
        --------
        The following example creates 100 MIDI notes on take in
        reversed order, with ``sort=False`` for efficiency. Thus,
        ``take.notes`` is not time-sorted. ``take.sort_events`` is
        called afterwards so that ``take.notes`` is time-sorted.

        >>> for i in range(100):
        ...     take.add_note(99 - i, 100 - i, pitch=0, sort=False)
        ...
        >>> take.notes[0].start, take.notes[1].start
        99.0, 98.0
        >>> take.sort_events()
        >>> take.notes[0].start, take.notes[1].start
        0.0, 1.0
        """
        RPR.MIDI_Sort(self.id)

    @property
    def source(self):
        """
        Take source.

        :type: Source
        """
        return reapy.Source(RPR.GetMediaItemTake_Source(self.id))

    @property
    def start_offset(self):
        """
        Start time of the take relative to start of source file.

        :type: float
        """
        return self.get_info_value("D_STARTOFFS")

    def time_to_ppq(self, time):
        """
        Convert time in seconds to MIDI ticks.

        Parameters
        ----------
        time : float
            Time to convert in seconds.

        Returns
        -------
        ppq : float
            Converted time in MIDI ticks.

        See also
        --------
        Take.ppq_to_time
        """
        ppq = RPR.MIDI_GetPPQPosFromProjTime(self.id, time)
        return ppq

    @property
    def track(self):
        """
        Parent track of take.

        :type: Track
        """
        track_id = RPR.GetMediaItemTake_Track(self.id)
        return reapy.Track(track_id)

    def unselect_all_midi_events(self):
        """
        Unselect all MIDI events.

        See also
        --------
        Take.select_all_midi_events
        """
        self.select_all_midi_events(select=False)

    @property
    def visible_fx(self):
        """
        Visible FX in FX chain if any, else None.

        :type: FX or NoneType
        """
        with reapy.inside_reaper():
            return self.fxs[RPR.TakeFX_GetChainVisible(self.id)]
