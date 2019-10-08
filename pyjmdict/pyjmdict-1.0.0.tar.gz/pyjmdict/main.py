import lxml.etree as etree
from gzip import GzipFile
from .processor.jmdict   import JMDictProcessor
from .processor.kanjidic import KanjiDicProcessor
from jikan_sqlalchemy_utils.session import SessionMaker
from sys import stderr
from .db.jmdict import Base

def iterparse_clearing(filename_or_file):
    """Yield elements from *filename_or_file* xml incrementally, \
while clearing reference from the root node to its children to allow them \
to be garbage collected. This assumes that the xml file contains a \
single root node with many (direct) children."""
    # parser = etree.XMLParser(resolve_entities=False)
    context = iter(etree.iterparse(
        filename_or_file, events=('start', 'end'),
        resolve_entities=False))
    _, root = next(context) # get root element
    for event, elem in context:
        if event == 'end':
            yield elem
            if len(root):
                root.clear() # free memory

def yield_per(query, n=100):
    '''
like the `yield_per` method, but doesn't keep the cursor busy.
the SQL query must have a well-defined order'''
    i = 0
    while True:
        xs = tuple(query.slice(i, i+n).all())
        yield from xs
        if len(xs) < n:
            break
        i += n

def cross_reference(sm):
    from .db.kanjidic import Character
    from .db.jmdict import KanjiEntry, KanjiCharacterAssociation

    S = sm()
    q = S.query(KanjiCharacterAssociation)
    q.delete()
    S.commit()

    S = sm()
    to_be_saved = []
    def flush():
        S.bulk_save_objects(to_be_saved)
        S.commit()
        to_be_saved.clear()

    q = S.query(Character)

    qke = S.query(KanjiEntry).order_by(KanjiEntry.entry_id, KanjiEntry.i)
    for idx, ke in enumerate(yield_per(qke, n=10)):
        entry_id = ke.entry_id
        ke_i     = ke.i
        for c in frozenset(str(ke)):
            char = q.get(c)
            if char is not None:
                to_be_saved.append(KanjiCharacterAssociation(
                    entry_id=entry_id, ke_i=ke_i,
                    str=char.str))
        if len(to_be_saved) >= 1000:
            print("{:>7d}".format(idx), file=stderr)
            flush()
    flush()

def jmdict_parse(session, stream):
    p = JMDictProcessor(session=session)
    n = 0
    for e in iterparse_clearing(stream):
        if e.tag == 'entry':
            p.process_entry(e)
            n += 1
            if n % 500 == 0:
                print('{:>7d}'.format(n), file=stderr)
    p.flush(force=True)

def kanjidic_parse(session, stream):
    p = KanjiDicProcessor(session=session)
    n = 0
    for e in iterparse_clearing(stream):
        if e.tag == 'character':
            p.process_character(e)
            n += 1
            if n % 500 == 0:
                print('{:>7d}'.format(n), file=stderr)
    p.flush(force=True)

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description=("Generate EDICT sqlite db."))
    parser.add_argument('--drop-all', action='store_true',
                        help='drop all pyjmdict tables')
    parser.add_argument('--jmdict',
                        help='path to EDICT "JMdict.xml.gz"')
    parser.add_argument('--kanjidic',
                        help='path to EDICT "kanjidic2.xml.gz"')
    parser.add_argument('--crossref', action='store_true',
                        help='cross-reference jmdict and kanjidic')
    parser.add_argument('-u', '--pyjmdict-db', required=True,
                        help='file from which to read database URI')
    args = parser.parse_args()

    sm = SessionMaker.from_uri_filename(
        args.pyjmdict_db, isolation_level='SERIALIZABLE')

    # drop all tables
    if args.drop_all:
        Base.metadata.drop_all(sm().bind)

    sm.populate(Base)

    if args.kanjidic:
        with open(args.kanjidic, 'rb') as compressed_h, \
             GzipFile(fileobj=compressed_h) as h:
            kanjidic_parse(sm(), h)

    if args.jmdict:
        with open(args.jmdict, 'rb') as compressed_h, \
             GzipFile(fileobj=compressed_h) as h:
            jmdict_parse(sm(), h)

    if args.crossref:
        cross_reference(sm.sessionmaker)

if __name__=='__main__':
    main()
