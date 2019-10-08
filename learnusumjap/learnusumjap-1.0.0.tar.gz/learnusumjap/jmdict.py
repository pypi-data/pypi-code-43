import xml.etree.ElementTree as ET
from .explain_reading import explain_reading_to_html, explain_reading_helper
import etreetools.lib as EL

def html_make_list_if_more_than_one(l, tagname='ol'):
    n = len(l)
    if n <= 1:
        return l
    else:
        ol = ET.Element(tagname)
        for x in l:
            li = ET.Element('li')
            EL.extend(li, x)
            ol.append(li)
        return (ol,)

def html_word_entry(S, kanji_entry):
    ke = kanji_entry
    k = str(ke)
    reading = str(ke.readings[0])
    senses = ke.senses

    eg = html_make_list_if_more_than_one(tuple(
        filter(len,
               ('; '.join(str(gloss) for gloss in se.glosses
                         if gloss.lang == 'eng')
                for se in senses))))
    return eg

def html_make_p(*args):
    p = ET.Element('p')
    for a in args:
        EL.extend(p, a)
    return p
