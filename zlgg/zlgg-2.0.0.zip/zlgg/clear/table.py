#对table型的清洗

from selenium import webdriver
from bs4 import BeautifulSoup 

htmlparser="lxml"
def clear_tb_non1(page):
    driver=webdriver.Chrome()

    page=page.replace("'",'\\\'')

    driver.execute_script("page='%s';document.write(page)"%page)

    driver.execute_script("""
     var re = document.getElementsByTagName('tr'); 
    for (var i = re.length-1;i >=0;i--) { 
    if (re[i].offsetWidth<10 | re[i].offsetHeight<10){
    re[i].remove();
    }
     }
    """)
    driver.execute_script("""
     var re = document.getElementsByTagName('td'); 
    for (var i = re.length-1;i >=0;i--) { 
    if ( re[i].offsetHeight<10){
    re[i].remove();
    }
     }
    """)
    page=driver.page_source
    driver.quit()
    return page 

#删除空行,空table
def clear_tb_non(page):

    soup=BeautifulSoup(page,htmlparser)
    tables=soup.find_all('table')
    for table in tables:
        if table.text.strip()=='':table.extract()
        trs=table.find_all('tr')
        for tr in trs:
            if tr.text.strip()=='':
                tr.extract()
            tds=tr.find_all('td')
            for td in tds:
                if td.text.strip()=='':
                    td.extract()
    page=str(soup)
    page=page.replace("<th>",'<td>').replace("</th>","</td>")
    return page 


#从page中提取无嵌套的table 返回tables的数组
def get_pure_tbs(page):
    if page is None:return None
    tbs=[]
    soup=BeautifulSoup(page,htmlparser)
    tables=soup.find_all('table')
    if len(tables)==0:return None

    if len(tables)==1:
        tbs=[str(tables[0])]
        return tbs

    for tb in tables:
        tbtmp=tb.find('table')
        if tbtmp is  None:
            tbs.append(str(tb))
            continue
        if len(tbtmp.text.strip())<10:continue
        tbs.append(str(tbtmp))
    if tbs==[]:return None
    return tbs

