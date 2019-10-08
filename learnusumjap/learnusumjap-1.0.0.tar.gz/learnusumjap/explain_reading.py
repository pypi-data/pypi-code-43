from .mora import (rendaku_possibilities,
                   recognize_conjugation)
import romkan
from pyjmdict.db.kanjidic import Character
from collections import namedtuple, OrderedDict
from itertools import chain
import functools
import numpy as np

try:
    import xml.etree.ElementTree as ElementTree
except ImportError:
    ElementTree = None

ja_readings = frozenset(('ja_on', 'ja_kun'))
def all_readings(character):
    # TODO: SQL
    for rmg in character.rms:
        yield from (x for x in rmg.readings
                    if x.type in ja_readings)

class BaseFragment(object):
    def get_costs(self, word, preword):
        '''must yield (partial_cost, length, result)
if word is "abcdef" and we are evaluating cost at i=2, then
this function will receive word="cdef" and preword="ab"'''
        return ()

def common_prefix_length(x, y):
    i = 0
    for i, (a, b) in enumerate(zip(x, y)):
        if a != b:
            break
    else:
        return i + 1
    return i

class Fragment(BaseFragment):
    readings = ()
    skip_costs = ()
    source_str = ...
    kanji_postword = ...
    kanji_preword  = ...
    def __init__(self, readings, skip_costs, source_str):
        self.readings   = readings
        self.skip_costs = skip_costs
        self.source_str = source_str
    def get_costs(self, word, preword):
        for r in self.readings:
            reading, cost = r.reading, r.cost
            if word.startswith(reading):
                if reading:
                    postreading = self.kanji_postword
                    z = common_prefix_length(r.okurigana, postreading)
                    n = recognize_conjugation(reading, r.okurigana,
                                              postreading)
                    m = recognize_conjugation(reading, r.okurigana,
                                              word[len(reading):])
                    if (not r.okurigana) or ((n or m) is not None) or z:
                        cost_ = (cost - z*2000 - (n or m or 0)*1000
                                 - 10*((n or m) is not None))
                        yield (len(reading), cost_, r)
                        if m:
                            yield (len(reading)+m, cost_,
                                   r._replace(reading=word[:len(reading)+m]))
                else:
                    yield (len(reading), cost, r)
            if (word.startswith('の') and preword.endswith('ん')
                and reading.startswith('お')): # 天皇
                reading2 = reading.replace('お', 'の', 1)
                if word.startswith(reading2):
                    yield (len(reading), cost,
                           r._replace(reading=reading2))
        for skip_length, cost in self.skip_costs:
            if skip_length <= len(word):
                yield (skip_length, cost, word[:skip_length])
        yield from super().get_costs(word, preword)

def explain_reading_algorithm(fragments, word):
    '''FIXME TODO documentation
'''
    len_fragments = len(fragments)
    len_word = len(word)

    # memoization is lazy man's dynamic programming
    @functools.lru_cache(maxsize=None)
    def f(frag_index, word_index):
        if frag_index == len_fragments and word_index == len_word:
            return (0, ())
        if frag_index >= len_fragments or  word_index >  len_word:
            return (np.inf, ())
        args = (word[word_index:],
                word[:word_index])
        results = []
        for length, cost, result in fragments[frag_index].get_costs(*args):
            tail_cost, tail_results = f(frag_index + 1,
                                        word_index + length)
            results.append((tail_cost + cost, (result,) + tail_results))
        if not len(results):
            return (np.inf, ())
        best = min(results, key=lambda x:x[0])
        return best
    return f(0, 0)

def link_fragments(fragments):
    '''note: modifies fragments in-place'''
    ss = tuple(normalize_to_hiragana(frag.source_str)
               for frag in fragments)
    acc = ''
    for frag, s in zip(fragments, ss):
        frag.kanji_preword = acc
        acc = acc + s
    acc = ''
    for frag, s in zip(reversed(fragments), reversed(ss)):
        frag.kanji_postword = acc
        acc = acc + s
    return fragments

identity = lambda x:x

def uniq(iterable, key=identity):
    seen = set()
    for x in iterable:
        k = key(x)
        if k not in seen:
            seen.add(k)
            yield x

@functools.lru_cache(maxsize=256)
def normalize_to_hiragana(s):
    return romkan.to_hiragana(romkan.to_kunrei(s))

ReadingPossibility = namedtuple(
    "ReadingPossibility",
    ['cost', 'reading', 'okurigana',
     'source', 'original'])

def split_okurigana(s):
    spl = s.split('.', 1)
    if len(spl) > 1:
        return tuple(spl)
    else:
        return (s, '')

def expand_possibilities(source, base_cost):
    def stage0():
        s = str(source)
        s = s.strip('-')
        reading, okurigana = split_okurigana(s)
        if okurigana:
            yield ReadingPossibility(
                base_cost, reading, okurigana,
                source, s)
        else:
            yield ReadingPossibility(
                base_cost, reading, '',
                source, s)

    def stage1():
        for r in stage0():
            r = r._replace(
                reading=normalize_to_hiragana(r.reading),
                okurigana=normalize_to_hiragana(r.okurigana))
            yield r
            for r_rendaku in rendaku_possibilities(r.reading):
                yield r._replace(reading=r_rendaku, cost=r.cost+50)

    def stage2():
        for r in stage1():
            yield r
            s = r.reading
            if s.endswith('つ') or s.endswith('く'):
                yield r._replace(reading=s[:-1]+'っ', cost=r.cost+100)

    yield from stage2()

ReadingAnnotation = namedtuple(
    "ReadingAnnotation",
    ['kanji', 'reading', 'okurigana', 'source', 'original'])

def explain_reading(chars, target_reading, override):
    if not len(chars): return ()
    penalty = tuple((i, (i+1)*(1000000-i)) for i in range(0,11))

    readings = (
        (((ReadingPossibility(cost=0, reading=c, okurigana='',
                              source=None, original=c),)
          if isinstance(c, str) else
          chain.from_iterable(
              (expand_possibilities(r, i*5))
              for i, r in enumerate(all_readings(c))))
         if j not in override else
         override[j])
        for j,c in enumerate(chars))

    # reading_dicts = tuple(reading_dicts)
    # print(reading_dicts[1], reading_dict_override)
    # print([list(x.keys()) for x in reading_dicts])

    readings = tuple(tuple(
        uniq(sorted(rs, key=lambda r:r.cost),
             key=lambda r:(r.reading, r.okurigana)))
                     for rs in readings)

    score, split = explain_reading_algorithm(link_fragments(tuple(
        Fragment(readings=rs,
                 skip_costs=(() if isinstance(c, str) else penalty),
                 source_str=str(c))
        for c,rs in zip(chars, readings))), target_reading)

    def process_single_result(char, r):
        if isinstance(r, str): # from skip entry
            return ReadingAnnotation(
                kanji     = str(char),
                reading   = r,
                okurigana = '',
                source    = None,
                original  = None)
        else:
            return ReadingAnnotation(
                kanji     = str(char),
                reading   = r.reading,
                okurigana = r.okurigana,
                source    = r.source,
                original  = r.original)

    return tuple(process_single_result(c, r)
                 for c, r in zip(chars, split))

def joinlist(inter, iterable):
    iterable = iter(iterable)
    yield next(iterable)
    for x in iterable:
        yield from inter
        yield x

def explain_reading_helper(S, word, reading):
    '''\
returns ReadingAnnotation'''
    q = S.query(Character)
    l = tuple((q.get(c) or c, None) for c in word)
    inter = ('', tuple(ReadingPossibility(cost=cost,
                                          reading=r,
                                          okurigana='',
                                          source=None,
                                          original='')
                       for r, cost in (('', 0),
                                       ('の', 10000))))
    l = tuple(joinlist((inter,), l))
    return explain_reading(
        tuple(x[0] for x in l), reading,
        {i: override for i, (c, override) in enumerate(l)
         if override is not None})

class _NoSourceReading(object):
    def __repr__(self):
        return '<NoSourceReading>'
    def __str__(self):
        return '×'

no_source_reading = _NoSourceReading()

ReadingColumn = namedtuple(
    'ReadingColumn',
    ('kanji', 'reading', 'source_reading', 'source_okurigana', 'source_red'))

def count_True_after(lst):
    r = []
    n = len(lst)
    j = n
    for i in reversed(range(n)):
        r.insert(0, j-i-1)
        if not lst[i]:
            j = i
    r.insert(0, j)
    return tuple(r)

def explain_reading_to_reading_columns(result):
    def process(R):
        c,r,src,orig = R.kanji, R.reading, R.source, R.original
        if orig is not None:
            o_r, o_oku = split_okurigana(normalize_to_hiragana(orig))
        else:
            o_r, o_oku = '', ''
        if not c:
            f = ReadingColumn('', r, '', '', False)
        elif orig is None:
            f = ReadingColumn(c, r, no_source_reading, '', True)
        elif orig == c:
            f = ReadingColumn(c, '', '', '', False)
        elif o_r == r:
            if o_oku:
                f = ReadingColumn(c, r, o_r, o_oku, False)
            else:
                f = ReadingColumn(c, r, '', '', False)
        else:
            f = ReadingColumn(c, r, o_r, o_oku, True)
        return f
    return tuple(process(R) for R in result if R.kanji or R.reading)

def explain_reading_to_text(result):
    cols = explain_reading_to_reading_columns(result)

    r = []
    a = r.append
    for R in cols:
        a(R.kanji)
        if R.reading:
            a("[")
            if R.source_reading or R.source_okurigana:
                o_r, oku, red = (str(R.source_reading), R.source_okurigana,
                                 R.source_red)
                if R.source_red: a("!")
                a(o_r)
                if oku: a('⋅'+oku)
                a("→")
            a(R.reading)
            a("]")
    return ''.join(r)

def explain_reading_to_html(result, class_prefix='fgn-',
                            ElementTree=ElementTree):
    def td(text, attrib=()):
        e = ElementTree.Element('td')
        e.text = text
        e.attrib.update(attrib)
        return e

    cssp = class_prefix

    tr = [ElementTree.Element('tr') for k in range(3)]
    cols = explain_reading_to_reading_columns(result)
    tr2_empty = [not (R.source_reading or R.source_okurigana) for R in cols]
    tr2_empty_after = count_True_after(tr2_empty)
    pre = tr2_empty_after[0]
    if pre > 0:
        tr[2].append(td('', {'colspan': str(pre)}))
    for i, R in enumerate(cols):
        color_class = cssp+'c{}'.format(i%3)
        k = R.kanji
        tr[0].append(td(k if k else '↓',
                        {'class': color_class if k else cssp+'extra'}))
        tr[1].append(td(R.reading, {'class': color_class}))
        if not tr2_empty[i]:
            o_r, oku, red = (str(R.source_reading), R.source_okurigana,
                             R.source_red)
            source_color_class = cssp+'red' if red else color_class
            append1, append2 = None, None
            colspan = tr2_empty_after[i+1]
            under = o_r
            if colspan > 0:
                d = {}
                if colspan > 1:
                    d['colspan'] = str(colspan)
                if oku:
                    d['class'] = cssp+'oku '+source_color_class
                append2 = (td('⋅'+oku if oku else None, d))
            elif oku: # no room for okurigana, ugh
                under = o_r+'⋅'+oku
            append1 = td(under, {'class': source_color_class})
            for a in (append1, append2):
                if a is not None:
                    tr[2].append(a)
    table = ElementTree.Element('table')
    table.extend(tr)
    table.attrib['class'] = cssp+'table'
    return (table,)

def explain_reading_to_html_css(class_prefix='fgn-'):
    return '''\
table.{p}table {{
vertical-align: top;
display: inline;
border-spacing: 0px;
border: none;
}}

table.{p}table tr {{
padding:0px;
margin:0px;
}}

table.{p}table td {{
padding:0px;
margin:0px;
text-align:center;
}}

table.{p}table tr:nth-child(1), table.{p}table tr:nth-child(1) > a {{
font-size:160%;
font-weight:normal;
color:black;
}}

table.{p}table td.{p}c0, table.{p}table td.{p}c0 > a {{
color:black;
}}

table.{p}table td.{p}c1, table.{p}table td.{p}c1 > a {{
color:green;
}}

table.{p}table td.{p}c2, table.{p}table td.{p}c2 > a {{
color:blue;
}}

table.{p}table tr:nth-child(2), table.{p}table tr:nth-child(3) {{
font-size: 100%;
}}

table.{p}table td.{p}extra, table.{p}table td.{p}extra > a {{
color:red;
font-size: 75%;
vertical-align: bottom;
}}

table.{p}table td.{p}red, table.{p}table td.{p}red > a {{
color:darkred;
}}

table.{p}table td.{p}oku {{
text-align: left;
}}
'''.format(p=class_prefix)
