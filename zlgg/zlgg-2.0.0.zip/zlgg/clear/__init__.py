#清晰文本page
from bs4 import BeautifulSoup 

from .ps import get_pure_ps 

from.table import get_pure_tbs ,clear_tb_non 
def clear_tag(page,tagname):
    soup=BeautifulSoup(page,'lxml')
    spans=soup.find_all(tagname)
    for span in spans:
            span.unwrap()
    return str(soup)

def clear_tags(page,exclude=None,include=None):
    arr=['span','font','b','u','strong']
    if exclude is not None:
        for w in exclude.split(','):arr.remove(w)
    if include is not None:
        for w in include.split(','):arr.append(w)
    for w in arr:

        page=clear_tag(page,w)
    return page



def tb_clear(page):
    page=clear_tags(page)
    page=clear_tb_non(page)
    tbs=get_pure_tbs(page)
    return tbs

def ps_clear(page):
    page=clear_tags(page)
    page=get_pure_ps(page)
    return page


