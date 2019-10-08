from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.ext.associationproxy import association_proxy, _AssociationList
from sqlalchemy import (String, Unicode, Integer, Boolean, Index,
                        ForeignKey, ForeignKeyConstraint, UniqueConstraint)
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import exc, relationship, aliased
import os
from jikan_sqlalchemy_utils import (
    SessionMaker, make_merge_args_class, OColumn,
    repr_helper, index, rel_to_query, pk_join_expr)
from contextlib import closing
import functools

import tqdm

from pyjmdict.db.jmdict   import KanjiEntry, ReadingEntry
from pyjmdict.db.kanjidic import Character

from .explain_reading_db import ExplainReadingCache
from .explain_reading import (explain_reading_to_text,
                              normalize_to_hiragana)

import sqlalchemy as sa
from concurrent.futures import ProcessPoolExecutor, as_completed


Base = declarative_base()
CA = make_merge_args_class(Base)

class WordExample(CA, Base):
    __tablename__ = 'kwe_word_example'

    id = OColumn(Integer, primary_key=True, _order=0)
    kanji   = OColumn(Unicode(  2), _order=10)
    word    = OColumn(Unicode( 64), _order=11)
    reading = OColumn(Unicode(128), _order=12)

    @declared_attr
    def __partial_table_args__(cls):
        return (index(cls, 'kanji'),
                index(cls, 'word'),
                index(cls, 'reading'))

def get_examples(pyjmdict_session,
                 explain_reading_cache, kanji):
    S = pyjmdict_session

    # c = S.query(Character).get(kanji)

    k1 = aliased(KanjiEntry, name='k1')
    sq = S.query(k1, func.count(ReadingEntry.entry_id).label('readings_count'))

    sq = (sq
          # .filter(k1.pri_nf != None)
          .join(k1.readings).group_by(k1)
          # .with_parent(c, 'kanji_entries') # doesn't work
          .filter(k1.str.like('%'+kanji+'%')) # FIXME: FUCKING STUPID!
          .subquery())

    k2 = aliased(KanjiEntry, name='k2')
    q3 = (S.query(k2, sq.c.readings_count)
          .select_from(sq)
          .join(k2, pk_join_expr(k2, sq))
          .filter(sq.c.readings_count == 1)
          .order_by(k2.pri_nf)
          .limit(200))

    seen_readings = set()
    good = []
    for ke, _ in q3.all():
        word, word_reading = str(ke), str(ke.readings[0])

        if S.query(KanjiEntry).filter(KanjiEntry.str == str(ke)).count() > 1:
            continue

        result = explain_reading_cache(pyjmdict_session,
                                       word, word_reading)

        # reject any irregular readings
        if any((a.kanji or a.reading) and a.source is None
               for a in result):
            continue

        try:
            ann = next(a for a in result if a.kanji==kanji)
        except StopIteration:
            continue

        reading = normalize_to_hiragana(ann.source.strip('-').partition('.')[0])
        if reading not in seen_readings:
            # print(reading, word, seen_readings, ann)
            seen_readings.add(reading)
            good.append(WordExample(
                kanji=kanji, word=word, reading=word_reading))

    return good

@functools.lru_cache(maxsize=8)
def init_pyjmdict(fn):
    return SessionMaker.from_uri_filename(
        fn, isolation_level='READ UNCOMMITTED')

@functools.lru_cache(maxsize=8)
def init_erc(fn):
    csm = SessionMaker.from_uri_filename(
        fn, isolation_level='READ COMMITTED')

    return ExplainReadingCache(cache_sessionmaker=csm)

@functools.lru_cache(maxsize=8)
def init_out(fn):
    osm = SessionMaker.from_uri_filename(
        fn, isolation_level='SERIALIZABLE')

    return osm

def do_db_init(args):
    osm = init_out(args.kwe_db)
    osm.populate(Base)

def do_kanji(args, kanji):
    psm = init_pyjmdict(args.pyjmdict_db)
    osm = init_out(args.kwe_db)
    erc = init_erc(args.erc_db)

    with closing(psm()) as sess:
        if sess.query(Character).get(kanji) is None:
            return

    for i in range(10):
        try:
            with closing(osm()) as out_session:
                if out_session.query(WordExample).filter(
                        WordExample.kanji == kanji).count():
                    return
            with closing(psm()) as pyjmdict_session:
                exs = list(get_examples(
                    pyjmdict_session=pyjmdict_session,
                    explain_reading_cache=erc,
                    kanji=kanji))
            with closing(osm()) as out_session:
                for ex in exs:
                    out_session.add(ex)
                out_session.commit()
        except sa.exc.ProgrammingError:
            pass
        else:
            break

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description=("generate kanji word example db"))
    parser.add_argument('--kanjis', required=True,
                        help='file containing kanjis')
    parser.add_argument('-j', '--jobs', type=int, default=None,
                        help='Allow N jobs at once.')
    parser.add_argument('-u', '--pyjmdict-db', required=True,
                        help='file from which to read pyjmdict database URI')
    parser.add_argument('-e', '--erc-db', required=True,
                        help='file from which to read explain-'
                        'reading cache database URI')
    parser.add_argument('-o', '--kwe-db', required=True,
                        help='file from which to read output database URI')
    args = parser.parse_args()

    kanjis = set()
    with open(args.kanjis, 'rt') as handle:
        while True:
            block = handle.read(1000)
            if not block: break
            kanjis.update(block)
            # break

    kanjis = list(sorted(kanjis))

    executor = ProcessPoolExecutor(max_workers=args.jobs)

    # init db
    executor.submit(do_db_init, args).result()

    futures = {executor.submit(do_kanji, args, kanji):
               kanji for kanji in kanjis}
    for future in tqdm.tqdm(as_completed(futures), total=len(futures)):
        kanji = futures[future]
        try:
            future.result()
        except Exception as exc:
            print('{!r} generated an exception'.format(kanji))
            raise

if __name__ == '__main__':
    main()

