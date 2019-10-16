# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 15:01:06 2019

@author: jittima
"""

import time
import ezsheets
import wget,os

class Gsheet:

    __NOM_PRENOMS = "Noms_Prenoms" #nom de la colonne nom_prenoms
    __OK = 'V'
    __NOK = 'X'
    __TAG_GROUP = 'Tag_group'

    def __init__(self,url_c,credential_id,**d):
        if not os.path.isfile('credentials-sheets.json'):
            wget.download('https://drive.google.com/uc?export=download&id='+credential_id,"credentials-sheets.json")
        self.__s = ezsheets.Spreadsheet(url_c)
        self.__url = url_c
        self.__group_tag = ""
        self.__group_class = ""
        self.__group_name = ""
        self.__start_row = 1
        self.__start_col = 1
        self.__all_group_class = list(self.__s.sheetTitles)
        self.__current_question = ''
        print("\nGsheet connected ...")
        print("Availables group_class: \n",self.__all_group_class)
        try:
            os.remove("credentials-sheets.json")
        except:
            pass
    
    def set_deco(self):
        def decorated(func):
            def wrapper(*args,**kwargs):
                currentQ = kwargs.get('question','')
                attempt = kwargs.get('attempt',-1)
                response = func(*args,**kwargs)
                if currentQ != '':
                    self.up(currentQ,response,attempt=attempt)
                else:
                    print("No question set ... no update")
                return response
            return wrapper
        return decorated
    
    def set_group_info(self,group_class,group_tag,group_name,start_row=1,start_col=1):
        assert group_class != '',"class group is incorrect"
        assert group_class in self.__all_group_class,f"class group not exist in sheet\nAvailable group class {self.__all_group_class} "
        assert group_tag !="","group tag must is incorrect"
        self.__sheet_nb = self.__all_group_class.index(group_class)
        self.__all_group_tags = self.__s.sheets[self.__sheet_nb].getColumn(self.__start_col)[1:15]
        assert group_tag in self.__all_group_tags,f"group tag not in sheet\nAvaillable tags {self.__all_group_tags}"
        assert group_name !="","group name must is incorrect"
        self.__group_tag = group_tag
        self.__group_class = group_class
        self.__group_name = group_name
        self.__start_col = start_col
        self.__start_row = start_row
        print(f"You are connected ... {self.__group_class}/{self.__group_tag}/{self.__group_name}")
        return self
    
    def get_start_col_row(self):
        return self.__start_col,self.__start_row
    
    def get_group_info(self):
        print(f"class name={self.__group_class}\ntag of the group={self.__group_tag}\nnames of group={self.__group_name}")
        return self.__group_class,self.__group_tag,self.__group_name
    
    def __update_group_result(self,question,result,**d):
        """
        update le gsheet définit par self
        arguments:
            question (str) : tag de la question à évaluer
            result (bool): résultat de la question - True False
            **d (unpack dict): 'time':True
                                'attempt':-1
        """
        if isinstance(result,bool):
            char_result = Gsheet.__OK if result else Gsheet.__NOK
        elif isinstance(result,str):
            char_result = result
        else:
            return None
        if question == '':
            print("no udate the sheet")
            return None       
        sh = self.__s.sheets[self.__sheet_nb]
        sh.refresh()
        col_r = list(sh.getRow(self.__start_row))[self.__start_col-1:].index(question.strip())+self.__start_col-1
        if col_r == -1:
            print(f"err01 - the question '{question}' not exist")
            return None
        row_r = list(sh.getColumn(self.__start_col))[self.__start_row-1:].index(self.__group_tag.strip())+self.__start_row-1
        if row_r == -1:
            print(f"err02 - the group name '{self.__group_tag}' not exist")
            return None
        t = time.strftime("%H:%M ", time.localtime()) if d.get('time',True) == True else ''
        old_result = sh.get(col_r+1,row_r+1) if d.get('start_new',False)==False else ""
        nb=d.get('attempt',-1)
        if nb>0 and (nb<=(old_result.count(Gsheet.__OK)+old_result.count(Gsheet.__NOK))):
            print("Maximum trying reached, can't change score")
            return None
        char = '' if old_result == '' else '|'
        arob = '@' if d.get('arobase',True)==True else ''
        sh.update(col_r+1,row_r+1,old_result+char+char_result+arob+t)
        sh.refresh() 
        return result
    
    def up(self,question,result,**d):
        return  self.__update_group_result(question,result,**d)
   

    def refresh(self):
        self.__s.refresh()

    def update_group_name(self):
        self.__update_group_result(Gsheet.__NOM_PRENOMS,self.__group_name,time=False,arobase=False,start_new=True)
        self.refresh()
        print("update name ... ok")
            
