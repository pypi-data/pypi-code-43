from zlgg.clear.table import get_pure_tbs
from bs4 import BeautifulSoup 
#from zlgg.clear.ps import get_pure_ps
import sys 

with open(sys.path[0]+'\\tb_clear_qt.html','r',encoding='utf8') as f :
    page=f.read()

def get_pure_ps(page):
    data=[]
    soup=BeautifulSoup(page,'lxml')
    tables=soup.find_all('table')
    if tables !=[]:
        for tb in tables:

                tb.extract()

    return str(soup)



tbs=get_pure_tbs(page)

ps=get_pure_ps(page)


with open(sys.path[0]+'\\test.html','w',encoding='utf8') as f :
    f.write(ps)
