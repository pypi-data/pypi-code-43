from itertools import product, chain
import operator
import romkan
from romkan import to_hiragana, to_kunrei
from .re_one_of import re_one_of
import re

vow = 'aiueo'
vow2 = tuple(vow) + ('ya', 'yo', 'yu')
con = 'kgsztdnhbpmr'
no_sokuon = set(vow2)
all_mora = set(map(lambda x: operator.add(*x),
                   product(con+'yw', vow)))
all_mora.update(vow)
all_mora.add("n'")
all_mora.add('xtu')
all_mora.add('vu')
all_mora.difference_update(('yi', 'ye', 'wi', 'wu', 'we'))
all_mora.update(p+'x'+v for v in vow2
                for p in chain((c+'i' for c in con), ('vu',)))
all_mora = dict((k, k) for k in all_mora)

all_mora = {k:to_hiragana(v).replace('う゛','ゔ')
            for k, v in all_mora.items()}
all_mora.update({'wi':'ゐ', 'we':'ゑ'})

def _make_conjugation_table():
    d = {}
    v5c = 'trkgbms'

    def e(form, *args):
        for arg in args:
            d.update(((form, k), v) for k, v in arg)

    e('polite', (('v1', ''), ('v5u', 'i')),
      (('v5'+k, k+'i') for k in v5c))

    e('negative', (('v1', 'nai'), ('v5u', 'wanai')),
      (('v5'+k, k+'anai') for k in v5c))

    for v, n in (('e', 'te'), ('a', 'perfective')):
        e(n,
          (('v1', 't'+v), ('v5k', 'it'+v), ('v5g', 'id'+v), ('v5s', 'sit'+v)),
          (('v5'+k, 'xtut'+v) for k in 'utr'),
          (('v5'+k,  "n'd"+v) for k in 'bm'))

    e('potential', (('v1', 'rareru'), ('v5u', 'eru')),
      (('v5'+k, k+'eru') for k in v5c))

    e('conditional', (('v1', 'reba'), ('v5u', 'eba')),
      (('v5'+k, k+'eba') for k in v5c))

    e('volitional', (('v1', 'you'), ('v5u', 'ou')),
      (('v5'+k, k+'ou') for k in v5c))

    e('passive',   (('v1', 'rareru'), ('v5u', 'wareru')),
      (('v5'+k, k+'areru') for k in v5c))

    e('causative', (('v1', 'saseru'), ('v5u', 'waseru')),
      (('v5'+k, k+'aseru') for k in v5c))

    e('prohibitive', (('v1', 'runa'), ('v5u', 'una')),
      (('v5'+k, k+'una') for k in v5c))

    e('imperative', (('v1', 'ro'), ('v5u', 'e')),
      (('v5'+k, k+'e') for k in v5c))

    return {k:to_hiragana(v) for k,v in d.items()}

conjugation_table = _make_conjugation_table()

def _print_conjugation_table():
    from tabulate import tabulate
    d = conjugation_table
    forms = tuple(sorted(set(form for form,stem in d.keys())))
    stems = tuple('v5'+a for a in 'utrkgbms') + ('v1',)
    F = to_kunrei
    return tabulate(tuple((s,)+tuple(F(d[(f, s)]) for f in forms)
                          for s in stems),
                    headers=("stem",)+tuple(f[:3] for f in forms),
                    tablefmt='simple')

def _make_potential_conjugations_table(forms_condition):
    d = {}
    econ = ('',) + tuple(con)
    with_u = tuple(('る',))
    with_u_re = re.compile("{}$".format(re_one_of(with_u)))
    for stems, s, prefixlen in chain(
            ((('v5u',)     ,      'u', 0),),
            ((('v5'+k,)    ,   k+ 'u', 0) for k in 'trkgbms'),
            ((('v1', 'v5r'), c+v+'ru', 1) for c in econ for v in 'ie')):
        a = frozenset(v for (form, stem), v
                      in conjugation_table.items()
                      if stem in stems and forms_condition(form))
        d[to_hiragana(s)] = (a | frozenset(with_u_re.sub(x, '') for x in a),
                             prefixlen)
    return d

potential_conjugations_table = _make_potential_conjugations_table(lambda form: True)

potential_pol_conjugations_table = _make_potential_conjugations_table(
    lambda form: form=='polite')

recognize_conjugation_re = re.compile("({})$".format(
    re_one_of(potential_conjugations_table.keys())))
def recognize_conjugation(reading, okurigana, postreading):
    ''' returns n where n is the number of matching
characters, or None if nonmatching '''
    if not okurigana:
        return None
    full = reading+okurigana
    m = recognize_conjugation_re.search(full)
    if not m:
        return None
    c = potential_conjugations_table.get(m.group(1), None)
    if c is None:
        return None
    conj, prefixlen = c
    okurigana_stem_end = (m.start(1) + prefixlen) - len(reading)
    if okurigana_stem_end < 0:
        return None
    postreading_conj = postreading[okurigana_stem_end:]
    for i in range(min(len(postreading_conj), 5), -1, -1):
        s = postreading_conj[:i]
        if s in conj:
            return i
    return None

# from wikipedia
rendaku_map = {'k': ('g',),
               's': ('z','j'),
               't': ('z','j','d'),
               'h': ('b','p')} # added 'p'; correct?

rendaku_actual_map = {to_hiragana(c+v):tuple(set(to_hiragana(nc+v)
                                                 for nc in ncs))
                      for c, ncs in rendaku_map.items()
                      for v in vow}

assert all(len(k)==1 for k in rendaku_actual_map)

def rendaku_possibilities(word):
    '''note: this does not return the original word'''
    c = word[0]
    replacements = rendaku_actual_map.get(c, None)
    if replacements is None:
        return ()
    else:
        suf = word[1:]
        return (r+suf for r in replacements)

split_mora_longest_re = re.compile('{}'.format(re_one_of(all_mora.values())))
def split_mora_longest(s):
    prev_end = 0
    r = []
    for m in re.finditer(split_mora_longest_re, s):
        if prev_end is not None:
            if m.start(1) != prev_end:
                break
        r.append(m.group(1))
        prev_end = m.end(1)
    return (prev_end, r)

def make_similarity_table(metric):
    d = {(xv, yv): metric(xk, yk)
         for xk, xv in all_mora.items()
         for yk, yv in all_mora.items()}

default_similarity_metric_strict = set(("n'", 'xtu'))
def default_similarity_metric(x, y):
    if x == y:
        return 2
    if set((x, y)) & default_similarity_metric_strict:
        return 0
    if x[0] == y[0]:
        return 1
    return 0

default_similarity_table = make_similarity_table(default_similarity_metric)
def similarity(a, b):
    '''returns (index_in_a, index_in_b)'''
    return (ae, be, (default_similarity_table.get(x_y, 0)
                     for x_y in zip(ar, br)))
