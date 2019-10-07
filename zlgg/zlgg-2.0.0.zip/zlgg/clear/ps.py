from bs4 import BeautifulSoup 
def get_pure_ps(page):
    data=[]
    soup=BeautifulSoup(page,'lxml')
    tables=soup.find_all('table')
    if tables !=[]:
        for tb in tables:
            tbtmp=tb.find('table')
            if tbtmp is  None:
                tds=tb.find_all('td')
                if tds==[]:
                    continue
                else:
                    v=len(tb.text)/len(tds)
                    v1=len(soup.text)/4
                    if v>v1:continue
                tb.extract()

    return str(soup)
