from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.associationproxy import association_proxy, _AssociationList
from sqlalchemy import (String, Unicode, Integer, Boolean, Index,
                        ForeignKey, ForeignKeyConstraint, UniqueConstraint)
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import exc, relationship
import os
from jikan_sqlalchemy_utils import (
    make_merge_args_class, OColumn, repr_helper, index)

from .explain_reading import ReadingAnnotation, explain_reading_helper

Base = declarative_base()
CA = make_merge_args_class(Base)

class Word(CA, Base):
    __tablename__ = 'er_word'

    id = OColumn(Integer, primary_key=True, _order=0)
    str     = OColumn(Unicode( 32), _order=10)
    reading = OColumn(Unicode(128), _order=11)

    annotations = relationship('Annotation', order_by='Annotation.i',
                               back_populates='word')

    @declared_attr
    def __partial_table_args__(cls):
        return (index(cls, 'str'),
                index(cls, 'reading'))

    def __repr__(self):
        return repr_helper('W', (
            (None, str(self)),
            ('reading', self.readings)))

class Annotation(CA, Base):
    __tablename__ = 'er_annotation'

    word_id = OColumn(Integer, ForeignKey(Word.__tablename__+".id"),
                      primary_key=True, _order=0)
    i = OColumn(Integer,
                primary_key=True, nullable=False, _order=1)

    kanji   = OColumn(Unicode(16), _order=10)
    reading = OColumn(Unicode(32), _order=11)
    okurigana = OColumn(Unicode(32), _order=12)
    source    = OColumn(Unicode(32), _order=13)
    original  = OColumn(Unicode(32), _order=14)

    word = relationship('Word', back_populates='annotations')

    @declared_attr
    def __partial_table_args__(cls):
        return (index(cls, 'kanji'),
                index(cls, 'reading'),
                index(cls, 'okurigana'),
                index(cls, 'source'),
                index(cls, 'original'))

    def __repr__(self):
        return repr_helper('R', (
            (None, self.kanji),
            (None, self.reading),
            ('okurigana', self.okurigana),
            ('source', self.source),
            ('original', self.original)))

    def to_reading_annotation(self):
        return ReadingAnnotation(
            **{k: getattr(k) for k in
               ReadingAnnotation._fields})

class ExplainReadingCache:
    def __init__(self, cache_sessionmaker):
        self.cache_sessionmaker = cache_sessionmaker
        self.populate_db()

    def populate_db(self):
        Base.metadata.create_all(self.cache_sessionmaker().bind)

    def actual_call(self, session, word, reading):
        return explain_reading_helper(session, word, reading)

    def __call__(self, session, word, reading):
        ses = self.cache_sessionmaker()
        try:
            w = ses.query(Word).filter(
                and_(Word.str == word,
                     Word.reading == reading)).first()

            if w is None:
                result = self.actual_call(session, word, reading)
                w = Word(str=word, reading=reading)
                ses.add(w)

                for a in (Annotation(
                    word=w, i=i,
                    kanji=ann.kanji,
                    reading=ann.reading,
                    okurigana=ann.okurigana,
                    source=None if ann.source is None else str(ann.source),
                    original=ann.original)
                              for i, ann in enumerate(result)):
                    ses.add(a)

            ses.commit()
            return list(w.annotations)
        finally:
            ses.close()

