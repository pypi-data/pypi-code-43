
# coding: utf-8

# In[3]:


import urllib2 
import urllib
from bs4 import BeautifulSoup
import json
import zlib
import json
import requests
from colorama import Fore, Back, Style 
import pprint
from texttable import Texttable
import re



url_Template="https://api.stackexchange.com/2.2{link}?order=desc&sort=votes&site=stackoverflow&filter=!-*jbN-FjhDuu&key=8v6rHdiTEj8xgsiVDC9ibA((&title="

def url_builder(base_url,title):
    
    for i in  title:
        if i>='a' and i<='z' :
            base_url+=i
        elif i>='A' and i<='Z' :
            base_url+=i
        else:
            base_url+='%'+format(ord(i), "X")
    return base_url

def get_request(url,title):
    req=urllib2.Request(url_builder(url,title))
    content=urllib2.urlopen(req).read()
    decompressed_data = zlib.decompress(content, 16+zlib.MAX_WBITS)
    return decompressed_data

def similar_questions_search(question):
#     print decompressed_data
    t = Texttable()
    json_data = json.loads(get_request(url_Template.replace("{link}","/similar"),question))
    s=""
    index=0
    for i in range(min(len(json_data["items"]),10)):
        if json_data["items"][i].get("title")!=None :
            s=""
            index=index+1
            s+="ques"+str(index)+" : "+BeautifulSoup(json_data["items"][i]["title"]).text+"\n"
            t.add_row([s])
            
            
    if index==0 :
        return "Sorry! We culdn't Find any Result"
    else:
        return t.draw()



# In[15]:
def get_answers(ques):
    t = Texttable()
    json_data = json.loads(get_request(url_Template.replace("{link}","/search/excerpts"),ques))
    index=0
    
    s=""
    for i in range(min(len(json_data["items"]),4)):
        if json_data["items"][i].get("answer_id")!=None :
            s=""
            index=index+1
            req1=urllib2.Request("https://api.stackexchange.com/2.2/posts/"+str(json_data["items"][i].get("answer_id"))+"?order=desc&sort=votes&site=stackoverflow&filter=!9Z(-wu0BT&key=8v6rHdiTEj8xgsiVDC9ibA((")
            content1=urllib2.urlopen(req1).read()
            decompressed_data1 = zlib.decompress(content1, 16+zlib.MAX_WBITS)
            json_data1 = json.loads(decompressed_data1)
            s+="ans"+str(index)+" : "+BeautifulSoup(json_data1["items"][0]["body"]).text+"\n"
            t.add_row([s])
    
    if index==0 :
        return "Sorry! We culdn't Find any Result"
    else:
        return t.draw()
def stack_menu():

	t=Texttable()
	t.add_row(["Menu"])
	t.add_row(["1: Search For Answer for a Question"])
	t.add_row(["2: Search For Questions Similar to the Question"])
	t.add_row(["3: Exit"])
	print t.draw()
	while True:
	    g = raw_input("Enter your Choice : ")
	    
	    if re.search('[^0-9]',g)!=None or not g:
	        print "Enter Valid Option"
	        continue
	    g=int(g,10)
	    
	    if g==3 :
	        break
	    else:
	        if g==1:
	            ques = raw_input("Enter The Question that you want to Search : ")
	            print get_answers(str(ques))+"\n"
	#             print ques
	        elif g==2:
	            ques = raw_input("Enter The Question that you want to Search : ")
	#             print ques
	            print similar_questions_search(str(ques))+"\m"
	        else:
	            print "Enter Valid Option"

#stack_menu()
# In[5]:


# In[6]:




# In[7]:



    


# In[8]:



# In[9]:


#     print s


# In[10]:


# print similar_questions_search("reverse")


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




