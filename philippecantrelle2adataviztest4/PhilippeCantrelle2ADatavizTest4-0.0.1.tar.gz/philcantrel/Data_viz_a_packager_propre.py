#!/usr/bin/env python
# coding: utf-8

# In[5]:


get_ipython().run_line_magic('matplotlib', 'inline')

import matplotlib 
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import math
from random import sample
import os
import matplotlib.image as mpimg 
from collections import Counter

import matplotlib.lines as mlines


class Viz():

    #Classe permettant de visualiser de facon assez rapide une base assez propre mais comportant encore des NaN/0

    print("convertissez vos donnees en csv svp")
    print("")
    print("Exemple : Test = Viz(df)")
    print("Test.lafonction(arguments)")
    print("")
    print("Evolution_2_annees(df1,df2, etablissements, colonne_a_visualiser,y_max = 1000000, y_min = 0) pour l'evolution entre deux annees")
    print("")
    print("apercu() pour avoir un resume complet de la base")
    print("")
    print("warn_col() pour connaitre les colonnes a fort taux de NaN ou de 0")
    print("")
    print("Corr() pour avoir la heatmap des correlations")
    print("")
    print("rentrer data, eventuellement changer taille_echantillon (taille du sample)")
    print("")
    print("une erreur est renvoyee si la taille du sample est > taille de la base")

    def __init__(self, data, taille_echantillon=1000):

        self.data = data
        self.taille_echantillon = taille_echantillon
        self.data_sample = self.data.sample(self.taille_echantillon)

    #rapide resume de la base

    def apercu(self):

        def get_mean(df, mode=False):

            # mode (bouléen) : pour avoir le mode des variables catégorielles

            res = []
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            for var in list(df):
                if df[var].dtypes in numerics:
                    res.append(df[var].mean())
                else:
                    if mode==False:
                        res.append(np.nan)
                    else:
                        res.append(Counter(df[var].dropna(axis=0)).most_common(1)[0][0])
            return res

        def get_se(df):
            res = []
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            for var in list(df):
                if df[var].dtypes in numerics:
                    res.append(df[var].var())
                else:
                    res.append(np.nan)
            return res

        def get_min(df):
            res = []
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            for var in list(df):
                if df[var].dtypes in numerics:
                    res.append(df[var].min())
                else:
                    res.append(np.nan)
            return res

        def get_max(df):
            res = []
            numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
            for var in list(df):
                if df[var].dtypes in numerics:
                    res.append(df[var].max())
                else:
                    res.append(np.nan)
            return res

        def get_occ_et_val_princi(df):
            res = []
            l=[]
            j=0
            for i in df.columns:
                l = list(df[i].value_counts().to_dict().items())[:min(3, len(df[i].value_counts()))]
                res.append(l)
               # for j in range(len(list(df[i].value_counts().to_dict().items())[:min(3, len(df[i].value_counts()))])):
               #     res.append(l[j])
            return res


        def indicator(df, mode=False, chemin2save = None):

            resume = pd.DataFrame(columns=['Variable', 'Type', 'Taux_NA',
                                      'Nb_unique','occ_et_val_princi', 'Moyenne', 'Variance',
                                      'Min',
                                      'Max'])
            resume['Variable'] = list(df)

            resume['occ_et_val_princi'] = get_occ_et_val_princi(df)

            resume['Type'] = list(df.dtypes)
            resume['Taux_NA'] = list(df.isnull().sum()/df.shape[0])
            resume['Nb_unique'] = [df[var].nunique() for var in list(df)]
            resume['Moyenne'] = get_mean(df, mode=mode)
            resume['Variance'] = get_se(df)
            #resume['Variance_normalisee'] = resume['Moyenne']/resume['Variance']
            resume['Min'] = get_min(df)
            resume['Max'] = get_max(df)
            if (chemin2save != None):
                resume.to_csv(chemin2save)
            return resume

        l_int = []
        l_str = []
        l_float = []

        for i in self.data_sample.columns:
            if self.data_sample[i].dtype == 'float64':
                l_float.append(i)

        for i in self.data_sample.columns:
            if self.data[i].dtype == 'object':
                    l_str.append(i)

        for i in self.data_sample.columns:
            if self.data[i].dtype == 'int64':
                 l_int.append(i)

        print('nombre de type float : ' + str(len(l_int)))
        print('nombre de type object : ' + str(len(l_str)))
        print('nombre de type int : ' + str(len(l_float)))
        print("-"*246)
        print("les dimensions")
        print("nombre de lignes :" + str(self.data.shape[0]) + "nombre de colonnes :" + str(self.data.shape[1]))
        print("-"*246)
        print("un tableau recapitulatif : ATTENTION --> sur un sample de 1000 !")
        return(indicator(self.data_sample))


    #la matrice des correlations

    def corr_matrix(self):
        return  self.data_sample.corr()

    #pour savoir quelles colonnes sont remplies de nan ou de 0    

    def warn_col(self):

        #renvoie les colonnes a fort taux de NaN ou de 0

        #on prend un seuil de 200 nan 
        #(soit on prend la un sample de la table de taille mille soit la table fait moins de 1000lignes)

        lnan_ou_0=[]

        for i in self.data.columns:
            s_nan=0
            s_0=0
            l=len(self.data[i])

            if l < 1000:
                for j in self.data[i]:
                    if pd.isnull(j):
                        s_nan += 1
                    elif j == 0:
                        s_0 +=1
                if s_nan > 200:
                    lnan_ou_0.append(i)
                elif s_0 > 200 :
                    lnan_ou_0.append(i)

            else :
                extrait = self.data[i].sample(1000)
                for j in extrait:
                    if pd.isnull(j):
                        s_nan += 1
                    elif j == 0 :
                        s_0 += 1
                if s_nan > 200:
                    lnan_ou_0.append(i)
                elif s_0 > 200 :
                    lnan_ou_0.append(i)
        print("voici la liste des colonnes a plus de 20% de NaN ou de 0")
        return(lnan_ou_0)          

    def Corr(self):
        #pour plot
        plt.figure(figsize=(12,10), dpi= 80)
        sns.heatmap(self.data.corr(), xticklabels=self.data.corr().columns, yticklabels=self.data.corr().columns, cmap='RdYlGn', center=0, annot=True)

        #deco
        plt.title('Heatmap des correlations', fontsize=22)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.show()

    def Evolution_2_annees(self,df1,df2, etablissements, colonne_a_visualiser, y_max = 1000000, y_min = 0):

        print("Attention on a remplace NaN par 0 !")

        ###################################################################
        ##### Creation de la nouvelle base pour tracer les evolutions #####
        ###################################################################

        #df1 = pd.read_csv("Prelevements_2016.csv", sep=";", encoding = 'latin-1')
        #df2 = pd.read_csv("Prelevements_2017.csv", sep=";", encoding = 'latin-1')

        Annee_1 = df1["Annee"][0]
        Annee_2 = df2["Annee"][0]

        df1.rename(columns={colonne_a_visualiser: colonne_a_visualiser + str(Annee_1) }, inplace=True)
        df2.rename(columns={colonne_a_visualiser: colonne_a_visualiser + str(Annee_2) }, inplace=True)

        new_df = df1.merge(df2, left_on=['Identifiant'], right_on=['Identifiant'])
        new_def_no_nan = new_df.fillna(0)

        ###########################################################
        ##### Debut du code de la future fonction en lui meme #####
        ###########################################################

        # importation des data
        df = new_def_no_nan[new_def_no_nan[colonne_a_visualiser + str(Annee_1)] != 0]
        df = df[df[colonne_a_visualiser + str(Annee_2)] != 0]
        df['is_in'] = df.Nom_Etablissement_x.apply(lambda x: x in etablissements)
        df = df[df.is_in == True]

        left_label = [str(c) + ', '+ str(round(y)) for c, y in zip(df.Nom_Etablissement_x, df[colonne_a_visualiser + str(Annee_1)])]
        right_label = [str(c) + ', '+ str(round(y)) for c, y in zip(df.Nom_Etablissement_x, df[colonne_a_visualiser + str(Annee_2)])]
        klass = ['red' if (y1-y2) < 0 else 'green' for y1, y2 in zip(df[colonne_a_visualiser + str(Annee_1)], df[colonne_a_visualiser + str(Annee_2)])]

        # tracer les lignes
        def newline(p1, p2, color='black'):
            ax = plt.gca()
            l = mlines.Line2D([p1[0],p2[0]], [p1[1],p2[1]], color='red' if p1[1]-p2[1] > 0 else 'green', marker='o', markersize=6)
            ax.add_line(l)
            return l

        fig, ax = plt.subplots(1,1,figsize=(14,14), dpi= 80)

        # lignes verticales
        ax.vlines(x=1, ymin=y_min, ymax=y_max, color='black', alpha=0.7, linewidth=1, linestyles='dotted')
        ax.vlines(x=3, ymin=y_min, ymax=y_max, color='black', alpha=0.7, linewidth=1, linestyles='dotted')

        # points
        ax.scatter(y=df[colonne_a_visualiser + str(Annee_1)], x=np.repeat(1, df.shape[0]), s=10, color='black', alpha=0.7)
        ax.scatter(y=df[colonne_a_visualiser + str(Annee_2)], x=np.repeat(3, df.shape[0]), s=10, color='black', alpha=0.7)

        # annotations sur les lignes
        for p1, p2, c in zip(df[colonne_a_visualiser + str(Annee_1)], df[colonne_a_visualiser + str(Annee_2)], df['Nom_Etablissement_x']):
            newline([1,p1], [3,p2])
            ax.text(1-0.05, p1, c + ', ' + str(round(p1)), horizontalalignment='right', verticalalignment='center', fontdict={'size':14})
            ax.text(3+0.05, p2, c + ', ' + str(round(p2)), horizontalalignment='left', verticalalignment='center', fontdict={'size':14})

        # deco
        ax.set_title("evolution entre " + str(Annee_1) + " et " + str(Annee_2), fontdict={'size':22})
        ax.set_xticks([1,3])
        ax.set_xticklabels([colonne_a_visualiser + str(Annee_1), colonne_a_visualiser + str(Annee_2)])
        plt.yticks([])

        # Pour enlever les bords
        plt.gca().spines["top"].set_alpha(.0)
        plt.gca().spines["bottom"].set_alpha(.0)
        plt.gca().spines["right"].set_alpha(.0)
        plt.gca().spines["left"].set_alpha(.0)
        plt.show()


# In[ ]:




