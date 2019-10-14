import functools
import numpy

from ..base import Model
from ..core import Recording, SpikeChannel
from v2_dataset import mixins
from v2_dataset.orm import (
    Column,
    StrictForeignKey,
    mixins as orm_mixins,
    relationship,
    types,
)
from sqlalchemy import CheckConstraint, UniqueConstraint


class Sorting(
    Model, orm_mixins.PrimaryKey, orm_mixins.PolymorphicBase, mixins.SortedRecording
):

    recording_id = Column(types.Integer, StrictForeignKey(Recording.id), nullable=False)
    comment = Column(types.String(256))

    # recording = relationship(Recording, back_populates="all_sortings")

    @property
    def dir_path(self):
        return self.recording.path.parent / "sortings" / str(self.index)


class OtherSorting(Sorting, orm_mixins.PolymorphicDerived):
    id = Column(types.Integer, StrictForeignKey(Sorting.id), primary_key=True)


class SortedChannel(
    Model, orm_mixins.PrimaryKey, orm_mixins.PolymorphicBase, mixins.SortedChannel
):

    sorting_id = Column(types.Integer, StrictForeignKey(Sorting.id), nullable=False)
    spike_channel_id = Column(
        types.Integer, StrictForeignKey(SpikeChannel.id), nullable=False
    )
    spike_labels = Column(types.NumpyArray, nullable=False)

    spike_channel = relationship(SpikeChannel)

    __table_args__ = (UniqueConstraint(sorting_id, spike_channel_id),)

    @property
    def algorithm(self):
        return self.sorting.algorithm

    @property
    def dir_path(self):
        return (
            self.sorting.dir_path / "sorted_channels" / str(self.spike_channel.channel)
        )

    @property
    @functools.lru_cache(maxsize=None)
    def mask(self):
        mask = numpy.zeros(self.spike_channel.n_spikes, dtype=numpy.bool)
        for unit in self.sorted_units:
            mask[unit.mask] = True
        return mask


class SortedUnit(
    Model, orm_mixins.PrimaryKey, orm_mixins.PolymorphicBase, mixins.SortedUnit
):
    """Represents a single neuronal unit, obtained from a :class:`spike channel <v2.db.model.SpikeChannel>` by using a
    concrete :class:`spike sorting algorithm <v2.sorting.Algorithm>`. It is related to a corresponding
    :class:`v2.db.model.SortedChannel` entity and associated with a 1-based label that is unique among all units related
    to this sorted channel. It provides access to spike times, timestamps, and waveforms, which may be indexed by
    position or :class:`trial <v2.db.model.Trial>`.
    """

    sorted_channel_id = Column(
        types.Integer, StrictForeignKey(SortedChannel.id), nullable=False
    )
    label = Column(types.Integer, nullable=False)
    n_spikes = Column(types.Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(sorted_channel_id, label),
        CheckConstraint(label > 0),
        CheckConstraint(n_spikes > 0),
    )


Model.relate_1_to_n(Recording, Sorting, "sortings", "recording")
Model.relate_1_to_n(Sorting, SortedChannel, "sorted_channels", "sorting")
Model.relate_1_to_n(SortedChannel, SortedUnit, "sorted_units", "sorted_channel")
Recording.other_sortings = relationship(OtherSorting, back_populates="recording")
