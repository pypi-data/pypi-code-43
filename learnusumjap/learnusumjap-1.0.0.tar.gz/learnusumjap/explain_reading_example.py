from jikan_sqlalchemy_utils.session import SessionMaker
from pyjmdict.db.jmdict import *
from pyjmdict.db.kanjidic import *
import sqlalchemy as sa
from sqlalchemy import func, and_, or_
from sqlalchemy.orm import aliased
from sqlalchemy.inspection import inspect
from .sau_fixed import get_primary_keys
import json
from collections import OrderedDict, namedtuple
from .explain_reading import (explain_reading_helper, explain_reading_to_text,
                              explain_reading_to_html,
                              explain_reading_to_html_css)
from .explain_reading_db import ExplainReadingCache
import xml.etree.ElementTree as ET
from .jmdict import html_make_p, html_word_entry

def main():
    with open('Heisigs_RTK_6th.json') as handle:
        heisig = json.load(handle)
    sm = SessionMaker.from_uri_filename('database.txt')

    csm = SessionMaker.from_sqlite_filename(
        "cache.sqlite", isolation_level='SERIALIZABLE')

    erc = ExplainReadingCache(cache_sessionmaker=csm)

    S = sm()
    qke = S.query(KanjiEntry)
    q = S.query(KanjiEntry).filter(KanjiEntry.pri_nf <= 40)
    q = q.order_by(func.length(KanjiEntry.str).desc())
    q = q.limit(1200)
    print(HEADER)

    for ke in q.all():
        print(ET.tostring(html_make_p(
            explain_reading_to_html(
                erc(S, str(ke), str(ke.readings[0])))
            +(' ',)+html_word_entry(S, ke)), 'unicode'))
    print('''</body>
</html>
''')

HEADER = '''<html lang="en">
  <meta charset="utf-8">
  <head>
    <style>{}

body {{
font-family: "Noto Sans", "Noto Sans CJK JP", sans-serif;
}}
</style>
  </head>
  <body>
'''.format(explain_reading_to_html_css())

if __name__=='__main__':
    main()

