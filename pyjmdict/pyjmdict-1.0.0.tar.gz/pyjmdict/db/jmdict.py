from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.associationproxy import association_proxy, _AssociationList
from sqlalchemy import (String, Unicode, Integer, Boolean, Index,
                        ForeignKey, ForeignKeyConstraint, UniqueConstraint)
from sqlalchemy.orm import exc, relationship
import os
from jikan_sqlalchemy_utils import (
    make_merge_args_class, OColumn, repr_helper, index)

Base = declarative_base()
CA = make_merge_args_class(Base)

# note that columns named "i" refer to the index of the child in its parent

class StrColumnMixin:
    _str_len = 8

    @declared_attr
    def str(cls):
        return OColumn(Unicode(cls._str_len), _order=10)

    def __str__(self):
        return self.str

class IdxStrColumnMixin(StrColumnMixin):
    @declared_attr
    def __partial_table_args__(cls):
        return (index(cls, 'str'),)

class DictionaryEntry(Base):
    __tablename__ = 'd_entry'

    id = OColumn(Integer, primary_key=True, _order=0) # ent_seq
    kanjis   = relationship("KanjiEntry"  , back_populates="parent_entry")
    readings = relationship("ReadingEntry", back_populates="parent_entry")
    senses   = relationship("Sense"       , back_populates="parent_entry")

    def __repr__(self):
        return repr_helper('E', (
            ('ent_seq', self.id),
            ('kanjis', self.kanjis),
            ('readings', self.readings),
            ('senses', self.senses)))

pri_keys = ['news', 'ichi', 'spec', 'gai', 'nf']

class PriorityMixin:
    pri_news = OColumn(Integer, nullable=True, _order=50)
    pri_ichi = OColumn(Integer, nullable=True, _order=51)
    pri_spec = OColumn(Integer, nullable=True, _order=52)
    pri_gai  = OColumn(Integer, nullable=True, _order=53)
    pri_nf   = OColumn(Integer, nullable=True, _order=54)

    @declared_attr
    def __partial_table_args__(cls):
        return (index(cls, 'pri_news'),
                index(cls, 'pri_ichi'),
                index(cls, 'pri_spec'),
                index(cls, 'pri_gai'),
                index(cls, 'pri_nf'))

    def _pri_kw(self):
        return tuple((k, getattr(self, 'pri_'+k))
                     for k in pri_keys)

class DictionaryEntryChildMixin:
    @declared_attr
    def entry_id(cls):
        return OColumn(Integer, ForeignKey("d_entry.id"),
                       nullable=False, primary_key=True, _order=0)
    @declared_attr
    def i(cls):
        return OColumn(Integer,
                       nullable=False, primary_key=True, _order=1)

class KanjiReadingAssociation(CA, Base): # re_restr
    __tablename__  = 'd_kr'

    @declared_attr
    def __partial_table_args__(cls):
        return (
            ForeignKeyConstraint(
                [     'entry_id',   'ke_i'],
                ['d_ke.entry_id', 'd_ke.i']),
            ForeignKeyConstraint(
                [     'entry_id',   're_i'],
                ['d_re.entry_id', 'd_re.i']),
            index(cls, 'er', 'entry_id', 're_i'),
            index(cls, 'ek', 'entry_id', 'ke_i'))

    entry_id = OColumn(Integer, primary_key=True, _order=0)
    ke_i     = OColumn(Integer, primary_key=True, _order=1)
    re_i     = OColumn(Integer, primary_key=True, _order=2)

    @declared_attr
    def ke(cls):
        return relationship("KanjiEntry", viewonly=True)
    @declared_attr
    def re(cls):
        return relationship("ReadingEntry", viewonly=True)

    def __repr__(self):
        return repr_helper('KR', (
            ('ent_seq', self.entry_id),
            ('ke_i', self.ke_i),
            ('re_i', self.re_i)))

class KanjiCharacterAssociation(CA, IdxStrColumnMixin, Base): # re_restr
    __tablename__  = 'dk_kc'

    @declared_attr
    def __partial_table_args__(cls):
        return (
            ForeignKeyConstraint(
                [     'entry_id',   'ke_i'],
                ['d_ke.entry_id', 'd_ke.i']),
            ForeignKeyConstraint(
                ['str'],
                ['k_c.str']),
            index(cls, 'ek', 'entry_id', 'ke_i'))

    entry_id = OColumn(Integer,    primary_key=True, _order=0)
    ke_i     = OColumn(Integer,    primary_key=True, _order=1)
    str      = OColumn(Unicode(4), primary_key=True, _order=2)

    @declared_attr
    def ke(cls):
        return relationship("KanjiEntry", viewonly=True)

    @declared_attr
    def character(cls):
        return relationship("Character", viewonly=True)

    def __repr__(self):
        return repr_helper('KC', (
            ('ent_seq', self.entry_id),
            ('ke_i', self.ke_i),
            ('c', self.str)))

class SenseKanji(CA, Base):
    __tablename__  = 'd_sk'

    @declared_attr
    def __partial_table_args__(cls):
        return (
            ForeignKeyConstraint(
                [     'entry_id',   'ke_i'],
                ['d_ke.entry_id', 'd_ke.i']),
            ForeignKeyConstraint(
                [     'entry_id',   'se_i'],
                ['d_se.entry_id', 'd_se.i']),
            index(cls, 'entry_id'))

    entry_id = OColumn(Integer, primary_key=True, _order=0)
    se_i     = OColumn(Integer, primary_key=True, _order=1)
    ke_i     = OColumn(Integer, primary_key=True, _order=2)

    @declared_attr
    def se(cls):
        return relationship("Sense", viewonly=True)
    @declared_attr
    def ke(cls):
        return relationship("KanjiEntry", viewonly=True)

class SenseReading(CA, Base):
    __tablename__  = 'd_sr'

    @declared_attr
    def __partial_table_args__(cls):
        return (
            ForeignKeyConstraint(
                [     'entry_id',   're_i'],
                ['d_re.entry_id', 'd_re.i']),
            ForeignKeyConstraint(
                [     'entry_id',   'se_i'],
                ['d_se.entry_id', 'd_se.i']),
            index(cls, 'entry_id'))

    entry_id = OColumn(Integer, primary_key=True, _order=0)
    se_i     = OColumn(Integer, primary_key=True, _order=1)
    re_i     = OColumn(Integer, primary_key=True, _order=2)

    @declared_attr
    def se(cls):
        return relationship("Sense", viewonly=True)
    @declared_attr
    def re(cls):
        return relationship("ReadingEntry", viewonly=True)

class KanjiEntry(CA, PriorityMixin, IdxStrColumnMixin,
                 DictionaryEntryChildMixin, Base):
    __tablename__  = 'd_ke'

    @declared_attr
    def parent_entry(cls):
        return relationship("DictionaryEntry", back_populates="kanjis")

    @declared_attr
    def readings(cls):
        return relationship(
            "ReadingEntry", secondary=KanjiReadingAssociation.__table__,
            viewonly=True)

    @declared_attr
    def senses(cls):
        return relationship(
            "Sense", secondary=SenseKanji.__table__,
            viewonly=True)

    @declared_attr
    def characters(cls):
        return relationship(
            "Character", secondary=KanjiCharacterAssociation.__table__,
            viewonly=True)

    str = OColumn(Unicode(32), _order=10)

    def __repr__(self):
        return repr_helper('K', ((None, self.str),) + tuple(self._pri_kw()))

class ReadingEntry(CA, PriorityMixin, IdxStrColumnMixin,
                   DictionaryEntryChildMixin, Base):
    __tablename__  = 'd_re'

    @declared_attr
    def parent_entry(cls):
        return relationship("DictionaryEntry", back_populates="readings")

    @declared_attr
    def kanjis(cls):
        return relationship(
            "KanjiEntry", secondary=KanjiReadingAssociation.__table__,
            viewonly=True)

    @declared_attr
    def senses(cls):
        return relationship(
            "Sense", secondary=SenseReading.__table__,
            viewonly=True)

    str          = OColumn(Unicode(64), _order=10)
    true_reading = OColumn(Boolean,     _order=11)

    def __repr__(self):
        return repr_helper('R', ((None, self.str),) + tuple(self._pri_kw()) + (
            ('not_true_reading', not self.true_reading),))

def _assoc_proxy_str(attr):
    return association_proxy(attr+'_', 'str')

def _sense_rel_helper(name):
    k = "Sense"+name
    return relationship(k, back_populates="sense", order_by=k+'.i')

class Sense(CA, DictionaryEntryChildMixin, Base):
    __tablename__ = 'd_se'

    parent_entry = relationship("DictionaryEntry", back_populates="senses")

    xrefs_           = _sense_rel_helper("XRef")
    antonyms_        = _sense_rel_helper("Antonym")
    parts_of_speech_ = _sense_rel_helper("POS")
    fields_          = _sense_rel_helper("Field")
    miscs_           = _sense_rel_helper("Misc")
    lsources         = _sense_rel_helper("LSource")
    dialects_        = _sense_rel_helper("Dialect")
    glosses          = _sense_rel_helper("Gloss")
    infos_           = _sense_rel_helper("Info")

    xrefs           = _assoc_proxy_str('xrefs')
    antonyms        = _assoc_proxy_str('antonyms')
    infos           = _assoc_proxy_str('infos')
    parts_of_speech = _assoc_proxy_str('parts_of_speech')
    fields          = _assoc_proxy_str('fields')
    miscs           = _assoc_proxy_str('miscs')
    dialects        = _assoc_proxy_str('dialects')

    @declared_attr
    def kanjis(cls):
        return relationship(
            "KanjiEntry", secondary=SenseKanji.__table__,
            viewonly=True)

    @declared_attr
    def readings(cls):
        return relationship(
            "ReadingEntry", secondary=SenseReading.__table__,
            viewonly=True)

    def __repr__(self):
        kw = (('pos', 'parts_of_speech'),
              ('fields', None),
              ('miscs', None),
              ('dial', 'dialects'),
              ('infos', None),
              ('glosses', None),
              ('lsrc', 'lsources'),
              ('xrefs', None),
              ('ant', 'antonyms'))
        return repr_helper(
            'sense', ((k, getattr(self, v if v else k)) for k,v in kw),
            ignore_empty=True)

class SenseChildMixin:
    @declared_attr
    def __partial_table_args__(cls):
        return (
            ForeignKeyConstraint(
                [     'entry_id',   'se_i'],
                ['d_se.entry_id', 'd_se.i']),)

    entry_id = OColumn(Integer, primary_key=True, _order=0)
    se_i     = OColumn(Integer, primary_key=True, _order=1)
    i        = OColumn(Integer, primary_key=True, _order=2)

    def __str__(self):
        return self.str

    def __repr__(self):
        return "<{} {!r}>".format(
            self.__class__.__name__, str(self))

class SenseXRef(CA, IdxStrColumnMixin, SenseChildMixin, Base):
    __tablename__ = 'd_se_xref'
    _tagname = 'xref'
    _str_len = 32*4

    @declared_attr
    def sense(cls):
        return relationship("Sense", back_populates="xrefs_")

class SenseAntonym(CA, IdxStrColumnMixin, SenseChildMixin, Base):
    __tablename__ = 'd_se_antonym'
    _tagname   = 'ant'
    _str_len = 16

    @declared_attr
    def sense(cls):
        return relationship("Sense", back_populates="antonyms_")

class SensePOS(CA, IdxStrColumnMixin, SenseChildMixin, Base):
    '''part of speech'''
    __tablename__ = 'd_se_pos'
    _tagname   = 'pos'
    _tagentity = True
    _str_len = 16

    @declared_attr
    def sense(cls):
        return relationship("Sense", back_populates="parts_of_speech_")

class SenseField(CA, IdxStrColumnMixin, SenseChildMixin, Base):
    '''field of application of sense'''
    __tablename__ = 'd_se_field'
    _tagname = 'field'
    _tagentity = True
    _str_len = 12

    @declared_attr
    def sense(cls):
        return relationship("Sense", back_populates="fields_")

class SenseMisc(CA, IdxStrColumnMixin, SenseChildMixin, Base):
    '''misc information for sense'''
    __tablename__ = 'd_se_misc'
    _tagname = 'misc'
    _tagentity = True
    _str_len = 8

    @declared_attr
    def sense(cls):
        return relationship("Sense", back_populates="miscs_")

class SenseLSource(CA, StrColumnMixin, SenseChildMixin, Base):
    '''loanword source'''
    __tablename__ = 'd_se_lsource'

    str     = OColumn(Unicode(256), _order=10)
    lang    = OColumn(Unicode(5),   _order=20)
    partial = OColumn(Boolean,      _order=21) # ls_type
    wasei   = OColumn(Boolean,      _order=22) # ls_wasei

    @declared_attr
    def sense(cls):
        return relationship("Sense", back_populates="lsources")

    def __repr__(self):
        return repr_helper('lsource', (
            (None, self.str)
            ('lang', self.lang or False),
            ('partial', self.partial),
            ('wasei', self.wasei)))

class SenseDialect(CA, IdxStrColumnMixin, SenseChildMixin, Base):
    '''dialect information for sense'''
    __tablename__ = 'd_se_dial'
    _tagname = 'dial'
    _tagentity = True
    _str_len = 8

    @declared_attr
    def sense(cls):
        return relationship("Sense", back_populates="dialects_")

class SenseGloss(CA, StrColumnMixin, SenseChildMixin, Base):
    __tablename__ = 'd_se_gloss'

    @declared_attr
    def __partial_table_args__(cls):
        return (index(cls, 'lang'),
                index(cls, 'gend'))

    str  = OColumn(Unicode(1024), _order=10)
    lang = OColumn(Unicode(   5), _order=20)
    gend = OColumn(Unicode(   5), _order=21, nullable=True)

    @declared_attr
    def sense(cls):
        return relationship("Sense", back_populates="glosses")

    def __repr__(self):
        return repr_helper('gloss', (
            (None, self.str),
            ('gend', self.gend or False),
            ('lang', self.lang or False)))

class SenseInfo(CA, IdxStrColumnMixin, SenseChildMixin, Base):
    __tablename__ = 'd_se_info'
    _tagname    = 's_inf'
    _str_len = 512

    @declared_attr
    def sense(cls):
        return relationship("Sense", back_populates="infos_")

class KanjiInf(CA, IdxStrColumnMixin, Base):
    __tablename__ = 'd_ke_inf'
    _str_len = 8

    @declared_attr
    def __partial_table_args__(cls):
        return (
            ForeignKeyConstraint(
                [     'entry_id',   'ke_i'],
                ['d_ke.entry_id', 'd_ke.i']))

    entry_id = OColumn(Integer, primary_key=True, _order=0)
    ke_i     = OColumn(Integer, primary_key=True, _order=1)
    i        = OColumn(Integer, primary_key=True, _order=2)

    def __repr__(self):
        return repr_helper('ke_inf', (
            (None, str(self)),
            ('ent_seq', self.entry_id),
            ('ke_i', self.ke_i),
            ('i', self.i)))

class ReadingInf(CA, IdxStrColumnMixin, Base):
    __tablename__ = 'd_re_inf'
    _str_len = 8

    @declared_attr
    def __partial_table_args__(cls):
        return (
            ForeignKeyConstraint(
                [     'entry_id',   're_i'],
                ['d_re.entry_id', 'd_re.i']),)

    entry_id = OColumn(Integer, primary_key=True, _order=0)
    re_i     = OColumn(Integer, primary_key=True, _order=1)
    i        = OColumn(Integer, primary_key=True, _order=2)

    def __repr__(self):
        return repr_helper('re_inf', (
            (None, str(self)),
            ('ent_seq', self.entry_id),
            ('re_i', self.ke_i),
            ('i', self.i)))
