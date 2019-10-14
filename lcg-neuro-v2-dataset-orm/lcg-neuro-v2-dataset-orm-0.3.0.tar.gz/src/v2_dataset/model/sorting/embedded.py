from ..base import Model
from ..core import Recording
from .core import Sorting
from sqlalchemy import UniqueConstraint
from v2_dataset.orm import Column, StrictForeignKey, mixins, relationship, types


class EmbeddedSorting(Sorting, mixins.PolymorphicDerived):
    id = Column(types.Integer, StrictForeignKey(Sorting.id), primary_key=True)

    # todo: I think this doesn't work.
    # __table_args__ = (
    #     UniqueConstraint(Sorting.recording_id),
    # )


Recording.embedded_sorting = relationship(
    EmbeddedSorting, back_populates="recording", uselist=False
)
