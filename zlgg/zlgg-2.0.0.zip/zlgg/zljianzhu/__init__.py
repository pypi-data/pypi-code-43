from bs4 import  BeautifulSoup 
import json 
# zhaobiaoren 
# zhongbiaoren    
# zbdl    
# zhongbiaojia    
# kzj 
# xmmc    
# xmjl    
# xmjl_zsbh   
# xmdz    
# zbfs    
# xmbh

soup=BeautifulSoup(page)


#xmmc
words=['项目名称']

xmmc=None 
for word in words:
        td=soup.find_all('td',attrs={'data-header':word})
        if td!=[]:
                xmmc= td[0].text.strip() 
                break  


#zhaobiaoren
words=['建设单位']

zhaobiaoren=None 
for word in words:
        td=soup.find_all('td',attrs={'data-header':word})
        if td!=[]:
                zhaobiaoren= td[0].text.strip() 
                break  

#zhongbiaoren
words=['中标单位名称']

zhongbiaoren=None 
for word in words:
        td=soup.find_all('td',attrs={'data-header':word})
        if td!=[]:
                zhongbiaoren= td[0].text.strip() 
                break  

#kzj
words=['总投资（万元）']

kzj=None 
for word in words:
        td=soup.find_all('td',attrs={'data-header':word})
        if td!=[]:
                kzj= td[0].text.strip() +'万元'
                break  



#zhongbiaojia
words=['中标金额（万元）','合同金额（万元）']

zhongbiaojia=None 
for word in words:
        td=soup.find_all('td',attrs={'data-header':word})
        if td!=[]:
                zhongbiaojia= td[0].text.strip() +'万元'
                break  


#zbdl
words=['招标代理单位名称']

zbdl=None 
for word in words:
        td=soup.find_all('td',attrs={'data-header':word})
        if td!=[]:
                zbdl= td[0].text.strip() 
                break  


#xmjl
words=['项目经理/总监理工程师姓名']

xmjl=None 
for word in words:
        td=soup.find_all('td',attrs={'data-header':word})
        if td!=[]:
                xmjl= td[0].text.strip() 
                break  


#xmjl_zsbh
words=['项目经理/总监理工程师身份证号码']

xmjl_zsbh=None 
for word in words:
        td=soup.find_all('td',attrs={'data-header':word})
        if td!=[]:
                xmjl_zsbh= td[0].text.strip() 
                break 


#xmjl
words=['项目编号']

xmbh=None 
for word in words:
        td=soup.find_all('td',attrs={'data-header':word})
        if td!=[]:
                xmbh= td[0].text.strip() 
                break  

result={"xmmc":xmmc,"zhaobiaoren":zhaobiaoren,"zhongbiaoren":zhongbiaoren,"kzj":kzj,"zhongbiaojia":zhongbiaojia,"zbdl":zbdl
,"xmjl":xmjl,"xmjl_zsbh":xmjl_zsbh,"xmbh":xmbh
}


result=json.dumps(result,ensure_ascii=False)
