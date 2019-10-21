# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 23:52:24 2019

@author: jazzn
"""
__autor__ = 'FJ'
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pyzik.pandly import y_to_str, SPY

def scatterCartoon(self, other_df=None, x='t', y ='X', titre = "", 
              ortho='auto', unsur=1, style_tracer='o',style='XKCD',
              color='auto', xlabel='', ylabel=''):
    couleur=['red', 'blue','green' , 'grey','darkgrey','gold','black',
             'pink','darkturquoise','lightblue','purple','maroon','violet','mistyrose']
    datf=[self]
    if not isinstance(y,list):
        y=[y]
    if not isinstance(other_df,list):
        other_df=[other_df]
    for elem in other_df:
        if isinstance(elem,pd.DataFrame):
            datf.append(elem)
    i=0
    if style.upper()=='XKCD':
        plt.xkcd()
    else:
        plt.rcdefaults() 
    for data in datf:
        try:
            nom = data.info
        except:
            nom = 'sans nom'
            print(f"Avertissement - dataframe sans nom\nEcrire ma_dataframe.info='quelque chose'")
            data.info = nom
        for ordonnee in y:
            a_virer = False
            if isinstance(ordonnee,float) or isinstance(ordonnee,int):
                a_virer = True
                txt=f'_val={ordonnee:.3e}'
                data[txt] = pd.Series(np.ones(len(data))*float(ordonnee))
                ordonnee=txt
                y[i]=txt
            plt.plot(data[x][::unsur],data[ordonnee][::unsur],color=couleur[i],label=f"{ordonnee}/({nom})")
            i = (i + 1)%len(couleur)
            if a_virer:
                data.drop(columns=[txt],inplace=True)
    if titre=="":
        try:
            titre="Courbe(s) relative(s) à "+" ; ".join([data.info for data in datf])
        except:
            titre="Pas de titre"
    plt.title(titre)
    if ortho=='ortho':
        plt.axis('equal')
    x_label = x if xlabel == '' else xlabel
    y_label = "-".join(y) if ylabel == '' else ylabel
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True, lw=0.5, zorder=0)
    plt.legend()
    global SPY
    SPY.append({'method':'scatterCartoon','x':x, 'y':y_to_str(y), 'ortho':ortho})
    return plt.show()

def restore_plt():
    return plt.rcdefaults()

def f_plot(x,y,titre='Courbe sans titre!!!',xlabel='pas de nom',ylabel='pas de nom',ortho='auto',style='xkcd'):
    """
    fonction qui retourne un graphique
    Arguments:
        * t (série numpy): nom de l'absisse
        * y (série numpy): nom des l'ordonnées (ex y=['y1','y2'])
        * titre (str): titre du tracé - Defaut 'Courbe sans titre!!!'
        * xlabel (str): nom de l'axe des absisses - Defaut 'pas de nom'
        * ylabel (str): nom de l'axe des ordonnées - Defaut 'pas de nom'
    
    Exemple : Soient y1, y2 et t des séries numpy de taille identique, pour tracer y1=f(t) et y2=f(t)
            > plot(t,y=[y1,y2],titre='y1=f(t) et y2=f(t)')
    """
    if isinstance(y,np.ndarray):
        y=[y]
    if style.upper()=='XKCD':
        plt.xkcd()
    else:
        plt.rcdefaults() 
    for i,elem in enumerate(y):
        plt.plot(x,elem,label=f"courbe n°{i}")
    plt.title(titre)
    if ortho == 'ortho':
        plt.axis('equal')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, lw=0.5, zorder=0)
    plt.legend()
    return plt.show()

pd.DataFrame.scatterCartoon = scatterCartoon
