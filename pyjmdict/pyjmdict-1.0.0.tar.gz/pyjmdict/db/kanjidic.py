from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.associationproxy import association_proxy, _AssociationList
from sqlalchemy import (String, Unicode, Integer, Boolean, Index,
                        ForeignKey, ForeignKeyConstraint, UniqueConstraint)
from sqlalchemy.orm import exc, relationship
import os
from collections import OrderedDict
from .jmdict import (Base, CA,
                     StrColumnMixin, IdxStrColumnMixin,
                     KanjiCharacterAssociation)
from .kanjidic_txt import dicref_keys
from jikan_sqlalchemy_utils import repr_helper, index, OColumn

_dr_str = set(('moro', 'oneill_names', 'busy_people_chapter'))
dicref_types = OrderedDict((k, dict(
    coltype=(Integer if k not in _dr_str else Unicode(8)),
    func=(int if k not in _dr_str else str)))
                           for k in dicref_keys)

DicRefMixin = type('DicRefMixin', (), {
    'dr_'+k: OColumn(v['coltype'], _order=i+50)
    for i,(k,v) in enumerate(dicref_types.items())})

cp_keys = ('ucs', 'jis208', 'jis212', 'jis213')

class Character(CA, DicRefMixin, Base):
    __tablename__  = 'k_c'
    str = OColumn(Unicode(4), primary_key=True, _order=0)

    cp_ucs    = OColumn(Integer, _order=10)
    cp_jis208 = OColumn(Integer, _order=11)
    cp_jis212 = OColumn(Integer, _order=12)
    cp_jis213 = OColumn(Integer, _order=13)

    radicals    = relationship("Radical",   back_populates="character")
    variants    = relationship("Variant",   back_populates="character")
    querycodes  = relationship("QueryCode", back_populates="character")
    rms         = relationship("RMGroup",   back_populates="character")
    nanori_     = relationship("Nanori",    back_populates="character")
    nanori      = association_proxy('nanori_', 'str')
    wrong_stroke_counts_ = relationship(
        "WrongStrokeCount", back_populates="character")
    wrong_stroke_counts  = association_proxy(
        "wrong_stroke_counts_", "stroke_count")
    radical_names_ = relationship(
        "RadicalName", back_populates="character")
    radical_names  = association_proxy(
        "radical_names_", "str")


    grade        = OColumn(Integer, _order=20)
    stroke_count = OColumn(Integer, _order=21)
    freq         = OColumn(Integer, _order=22)
    rad_name     = OColumn(Unicode, _order=23)
    jlpt         = OColumn(Integer, _order=24)

    def __str__(self):
        return self.str

    def __repr__(self):
        return repr_helper('character', (
            (None, str(self)),
            ('cp_ucs', self.cp_ucs),
            ('cp_jis208', self.cp_jis208),
            ('cp_jis212', self.cp_jis212),
            ('cp_jis213', self.cp_jis213),
            ('grade', self.grade),
            ('stroke_count', self.stroke_count),
            ('freq', self.freq),
            ('rad_name', self.rad_name),
            ('jlpt', self.jlpt),
            ('radicals', self.radicals),
            ('variants', self.variants),
            ('querycodes', self.querycodes),
            ('rms', self.rms),
            ('nanori', self.nanori)))

    @declared_attr
    def kanji_entries(cls):
        return relationship(
            "KanjiEntry", secondary=KanjiCharacterAssociation.__table__,
            viewonly=True)

class CharacterChildMixin:
    @declared_attr
    def character_id(cls):
        return OColumn(Unicode(4), ForeignKey(Character.__tablename__+'.str'),
                       nullable=False, primary_key=True, _order=0)

    @declared_attr
    def i(cls):
        return OColumn(Integer,
                       nullable=False, primary_key=True, _order=1)

    @declared_attr
    def character(cls):
        return relationship("Character", back_populates=cls._back_populates)

class Radical(CA, CharacterChildMixin, Base):
    __tablename__ = 'k_radical'
    _back_populates = 'radicals'
    value = OColumn(Integer,     _order=10)
    type  = OColumn(Unicode(16), _order=11)

    def __repr__(self):
        return repr_helper('rad', (
            (None, str(self.value)),
            ('type', self.type)))

class Variant(CA, CharacterChildMixin, IdxStrColumnMixin, Base):
    __tablename__ = 'k_variant'
    _back_populates = 'variants'
    str  = OColumn(Unicode(16), _order=10)
    type = OColumn(Unicode(16), _order=11)

    def __repr__(self):
        return repr_helper('var', (
            (None, str(self)),
            ('type', self.type)))

class WrongStrokeCount(CA, CharacterChildMixin, Base):
    __tablename__ = 'k_wrong_stroke_count'
    _back_populates = 'wrong_stroke_counts_'
    stroke_count = OColumn(Integer, _order=10)

    def __repr__(self):
        return repr_helper('wsc', ((None, str(self.stroke_count)),))

class RadicalName(CA, CharacterChildMixin, IdxStrColumnMixin, Base):
    __tablename__ = 'k_rad_name'
    _back_populates = 'radical_names_'
    str = OColumn(Unicode(16), _order=10)

    def __repr__(self):
        return repr_helper('rad', ((None, str(self)),))

class QueryCode(CA, CharacterChildMixin, IdxStrColumnMixin, Base):
    __tablename__ = 'k_querycode'
    _back_populates = 'querycodes'
    str  = OColumn(Unicode(16), _order=10)
    type = OColumn(Unicode(16), _order=11)
    skip_misclass = OColumn(Unicode(16), _order=12)

    def __repr__(self):
        return repr_helper('qc', (
            (None, str(self)),
            ('type', self.type),
            ('skip_misclass', self.skip_misclass or False)))

class Nanori(CA, CharacterChildMixin, IdxStrColumnMixin, Base):
    __tablename__ = 'k_nanori'
    _back_populates = 'nanori_'
    str = OColumn(Unicode(16), _order=10)

    def __repr__(self):
        return repr_helper('nanori', (
            (None, str(self)),))

class RMGroup(CA, CharacterChildMixin, Base):
    __tablename__ = 'k_rm'
    _back_populates = 'rms'
    readings = relationship("Reading", back_populates="rm")
    meanings = relationship("Meaning", back_populates="rm")

    def __repr__(self):
        return repr_helper('rmgroup', (
            ('readings', self.readings),
            ('meanings', self.meanings)))

class RMGroupChildMixin:
    @declared_attr
    def __partial_table_args__(cls):
        t = RMGroup.__tablename__
        return (
            ForeignKeyConstraint(
                [   'character_id', 'rm_i'],
                [t+'.character_id', t+'.i']),)

    @declared_attr
    def character_id(cls):
        return OColumn(Unicode(4), nullable=False, primary_key=True, _order=0)

    @declared_attr
    def rm_i(cls):
        return OColumn(Integer,    nullable=False, primary_key=True, _order=1)

    @declared_attr
    def i(cls):
        return OColumn(Integer,    nullable=False, primary_key=True, _order=2)

    @declared_attr
    def rm(cls):
        return relationship("RMGroup", back_populates=cls._back_populates)

class Reading(CA, RMGroupChildMixin, IdxStrColumnMixin, Base):
    __tablename__ = 'k_r'
    _back_populates = 'readings'
    str  = OColumn(Unicode(64), _order=10)
    type = OColumn(Unicode(8),  _order=11)
    on_type = OColumn(Unicode(8), _order=14)
    jouyou  = OColumn(Boolean,    _order=15)

    def __repr__(self):
        return repr_helper('kr', (
            (None, str(self)),
            ('type', self.type),
            ('on_type', self.on_type or False),
            ('jouyou', self.jouyou or False)))

class Meaning(CA, RMGroupChildMixin, StrColumnMixin, Base):
    __tablename__ = 'k_m'
    _back_populates = 'meanings'
    str  = OColumn(Unicode(128), _order=10)
    lang = OColumn(Unicode(5),  _order=20)

    def __repr__(self):
        return repr_helper('km', (
            (None, str(self)),
            ('lang', self.lang)))
