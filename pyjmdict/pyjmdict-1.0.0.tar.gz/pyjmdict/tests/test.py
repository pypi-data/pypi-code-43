
from ..main import kanjidic_parse, jmdict_parse, cross_reference
from ..processor.jmdict   import JMDictProcessor
from ..processor.kanjidic import KanjiDicProcessor
from jikan_sqlalchemy_utils.session import SessionMaker

from ..db.jmdict import DictionaryEntry, Base
from ..db.kanjidic import Character

import os
import unittest
import tempfile
from pkg_resources import resource_stream

class IncompleteTest(unittest.TestCase):
    def setUp(self):
        _, fn = tempfile.mkstemp(suffix='.jmdict_tmp')
        self.db_filename = fn
        self.sm = sm = SessionMaker.from_sqlite_filename(
            fn, isolation_level='SERIALIZABLE')

        sm.populate(Base)

        with resource_stream(__name__, 'kanjidic_sample.xml') as h:
            kanjidic_parse(sm(), h)

        with resource_stream(__name__, 'jmdict_sample.xml') as h:
            jmdict_parse(sm(), h)

        cross_reference(sm)

    def tearDown(self):
        os.remove(self.db_filename)

    def test_dict(self):
        q = self.sm().query
        tatoe = q(DictionaryEntry).get(1597120)

        k0 = tatoe.kanjis[0]
        r0 = tatoe.readings[0]

        self.assertEqual(k0.str, '例え')
        self.assertEqual(k0.pri_nf, 28)

        self.assertEqual(r0.str, 'たとえ')

        s0 = tatoe.senses[0]
        s0g0 = tatoe.senses[0].glosses[0]

        self.assertEqual(s0g0.str, 'example')
        self.assertEqual(s0g0.lang, 'eng')

        self.assertTrue('esp. 例え' in s0.infos)

    def test_kanji(self):
        q = self.sm().query
        rei = q(Character).get('例')
        rm0 = rei.rms[0]

        self.assertTrue(
            any(str(r)=='レイ' and r.type=='ja_on'
                for r in rm0.readings))
        self.assertTrue(
            any(str(m)=='example' and m.lang=='en'
                for m in rm0.meanings))

        self.assertTrue(set(str(ke) for ke in rei.kanji_entries)
                        .issuperset({'例え', '例外'}))


