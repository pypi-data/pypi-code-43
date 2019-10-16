# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 18:37:33 2019

@author: fj
"""
import pandas as pd
from prettytable import PrettyTable
from pyzik.pandly import f_input
from art import text2art
from skimage import io
import matplotlib.pyplot as plt
import random

class Quiz():
    def __init__(self,url_or_id,mode='gd',group='all',**d):
        """init a quiz instance
        Keyword arguments:
            url_or_id -- obvious (path of xlsx or url)
            mode -- if 'gd' load in google-drive and url_or_id is the id of xlsx
            group -- name of group in ur xlsx (default 'all' mean all groups)
        
        Example
            quiz = Quiz('quiz_formation.xlsx',mode='local',group='FEx1/FEx1Q1')
        """
        sheet_name = d.get('sheet_name','Feuil1')
        self.__url = url_or_id
        url = 'https://drive.google.com/uc?export=download&id='+self.__url if mode == 'gd' else url_or_id
        self.__quiz = pd.read_excel(url,sheet_name=sheet_name)
        cols = self.__quiz.columns
        self.__nb_Q = len(self.__quiz.index)
        self.__group,self.__tagQ,self.__Q,self.__media_url,self.__media_type,self.__BR = tuple(cols[0:6])
        print('groups availables = ',set(self.__quiz['Group']))
        if group != 'all':
            if '/' in group:
                groups = group.split('/')
                df = pd.DataFrame()
                for g in groups:
                    df = df.append(self.__quiz.loc[self.__quiz[self.__group]==g])
                self.__quiz = df
            else:
                self.__quiz = self.__quiz.loc[self.__quiz[self.__group]==group]
        self.__R = list(cols[6:-1])+[cols[-1]]
        self.__maxRep = len(cols)-6
        self.__startLetter = self.__R[0][0]
        self.__startNum = int(self.__R[0].replace(self.__startLetter,''))
        self.__quiz.fillna('',inplace=True)
        self.availableQ = list(self.__quiz.index)
        print(f"quiz uploaded ... {len(self.__quiz)} questions\nquestions index={self.availableQ}")
    
    def make_quiz(self,questions=None,group=None,glob_var = None,**d):
        """make a quiz and return score
            Keyword arguments:
                questions -- see example
                group -- name of selected group (default=None)
                glob_var -- usualy glob_val = globals() if use
            Examples:
                quiz of 15 questions in group='level0'
                    q.make_quiz(15,'level0',glob_var=globals())
                quiz of  questions number 1,2,3,4,9,26 in group='level1':
                    q.make_quiz([1,2,3,4,9,26],group='level1')
                quiz that tags are 'Q1' 'Q2' 'Q3':
                    q.make_quiz('Q1/Q2/Q3')
        """
        assert type(questions) in [int,list,str],"error,questions arg must be in 'list','str' or 'int' "
        if isinstance(questions,int): #si entier on choist sur l'ensemble du group
            if group != None:
                questions = random.sample(list(self.__quiz.loc[self.__quiz[self.__group]==group].index),k=questions)
            else:
                questions = random.sample(list(self.__quiz.index),k=questions)
        elif isinstance(questions,list):
                questions = random.sample(questions,k=len(questions))
        elif isinstance(questions,str):
                questions = self.__return_indexs(questions.split('/'))
                questions = random.sample(questions,k=len(questions))
        scores = [self.ask(i,glob_var=glob_var,**d) for i in questions]
        type_reply = d.get('typ','quiz')
        if type_reply == 'quiz':
            score = sum(scores)
            print(text2art("Score = "+str(score)+"/"+str(len(questions))))
            return score
        elif type_reply == 'text':
            return scores
    
    def isGlobal(self,index):
        return self.__quiz.at[index,self.__media_type] == "exec"
    
    def __get_rowR(self,index):
        return [self.__quiz.at[index,f"{self.__startLetter}{i}"] for i in range(self.__startNum,self.__startNum+self.__maxRep)]
    
    def __mix(self,index):
        lmix = random.sample([str(i+1) for i in range(self.__maxRep)],k=self.__maxRep)
        d= dict(zip(lmix,zip([str(i+1) for i in range(self.__maxRep)],self.__get_rowR(index))))
        return d
    
    def get_nbQ(self):
        return self.__nb_Q

    def __return_indexs(self,tagQ):
        if isinstance(tagQ,str):
            tagQ = [tagQ]
        return [self.__quiz.index[self.__quiz[self.__tagQ] == tag].tolist()[0] for tag in tagQ]
    
    def ask(self,index=None,**d):
        tagQ = d.get('tag','')
        if (tagQ != '') and (index == None):
            idxs = self.__quiz.index[self.__quiz[self.__tagQ] == tagQ].tolist()
            if len(idxs) == 0:
                print("Tag not exist")
                return
            else:
                index = idxs[0]
        try:
            Q = self.__quiz[self.__Q][index].replace(r'\n', '\n')
        except:
            print("question not exist")
            return None
        if index >= self.__nb_Q:
            print("question not exist")
            return None
        print(80*"-")
        print(text2art("Question  "+str(index),"bigfig"))
        print(80*"-"+"\n"+Q+'\n') #on écrit la question
        mediaType = self.__quiz.at[index,self.__media_type]
        if mediaType == 'img':
            mediaUrl = self.__quiz.at[index,self.__media_url]
            try:
                image = io.imread(mediaUrl)
                plt.imshow(image)
                plt.show()
            except:
                print("....")
                pass
        elif mediaType == 'exec':
            mediaUrl = self.__quiz.at[index,self.__media_url]
            try:
                exec(mediaUrl,d.get('glob_var',None))
            except:
                return True

        type_reply = d.get('typ','quiz')
        if type_reply == 'quiz':
            dd = self.__mix(index)
            rep_cols = [dd[str(i+1)][1] for i in range(self.__maxRep)]
            choix = [str(i+1) for i in range(self.__maxRep)]
            t = PrettyTable()
            t.add_column("choix",choix)
            t.add_column("reponse",rep_cols)
            t.align["reponse"] = "l"
            print(t);print('\n')
            result = f_input("Votre choix ?",output='str',choice=choix)
            rf = dd[result][0] in list(str(self.__quiz.at[index,self.__BR]))
            if rf:
                print(text2art("Bonne   reponse".upper(),'cybermedium'))
            else:
                print(text2art("Mauvaise   reponse".upper(),'cybermedium'))
            print(80*'-')
            return rf
        elif type_reply == 'text':
            tag = self.__quiz[self.__tagQ][index]
            responce = f_input("Votre réponse ?",output='str')
            return tag+'|'+responce if tag != '' else responce
        