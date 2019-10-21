# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 14:03:52 2019

@author: jazzn
"""
from prettytable import PrettyTable
from pyzik.pandly import f_input


class Menu():
    def __init__(self,title="My menu",list_menu=None):
        self.title = title
        if isinstance(list_menu,list):
            self.list_menu = list_menu
        else:
            self.list_menu = []
    
    def add_menu(self,sub_title,func=None):
        assert isinstance(sub_title,str),"sub title must be str"
        assert (func == None) or callable(func),"func arg isnt callable !! its not a function"
        self.list_menu.append([sub_title,func])
    
    def del_menu(self,s_text):
        """
        supprime le sous menu dont le sous-title contenant un extrait de s_text
        Exemple: toto_menu est un menu 
        +--------------------+
        | Menu               |
        +--------------------+
        | 0 - Calcul de i2   |
        | 1 - Calcul de n2   |
        | 2 - calcul de toto |
        | 3 - Exit           |
        +--------------------+
        Pour éliminer le sous menu 'calcul de toto' :
            > toto_menu.del_menu('ul de to') ou bien
            > toto_menu.del_menu('de toto') etc...
        """
        list_title = [self.list_menu[i][0] for i,_ in enumerate(self.list_menu)]
        for i,elem in enumerate(list_title):
            if s_text in elem:
                self.list_menu.pop(i)
                break
    
    def show(self):
        txt = PrettyTable()
        txt.field_names=[self.title]
        txt.align[self.title] = 'l'
        for i,val in enumerate(self.list_menu):
            v = f"{i} - {val[0]}"
            txt.add_row([v])
        n_max = len(self.list_menu)
        v = f"{n_max} - Exit"
        txt.add_row([v])
        print(txt) 
        while True:
            choix = f_input("select :","int",(0,n_max))
            if choix == n_max:
                break
            else:
                print(txt)
                try:
                    self.list_menu[choix][1]()
                except:
                    pass
