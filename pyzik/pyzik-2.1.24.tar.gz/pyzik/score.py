# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 21:44:01 2019

@author: jazzn
"""
import os
from datetime import datetime
import pandas as pd
from pyzik.pandly import f_input
from prettytable import PrettyTable

class Score:
    def __init__(self,name,group,test_info,path='T:'):
        assert name != '','name non null'
        assert group != '','group non null'
        assert test_info !='','test_info non null'
        self.file_name = path+'\\'+test_info+'_'+name+'_'+group+".csv"
        if not os.path.isfile(self.file_name):
            print("create score file ..."+self.file_name)
            f = open(self.file_name, 'a+')  # open file in append mode
            f.write(f"{80*'*'}\n{datetime.now().strftime('%d-%m-%Y')}\n{test_info}\n{80*'*'}\n")
            f.write("time;question;result;attempt\n")
            f.close()

    def up(self,question,response,attempt=-1):
        f = open(self.file_name, 'a+')  # open file in append mode
        f.write(f"{datetime.now().strftime('%H:%M:%S')};{question};{response};{attempt}\n")
        f.close()
        
    def set_deco(self):
        def decorated(func):
            def wrapper(*args,**kwargs):
                currentQ = kwargs.get('question','')
                attempt = kwargs.get('attempt',-1)
                response = func(*args,**kwargs)
                if currentQ != '':
                    print("up ....")
                    self.up(currentQ,response,attempt=attempt)
                else:
                    print("No question set ... no update")
                return response
            return wrapper
        return decorated

def generate_all(path='T:',test_info='TP01',dest_file='evalfinal_'):
    final_file = path+'\\'+dest_file+test_info+'.xlsx'
    df_tot = pd.DataFrame()
    print('list of files ...')
    for file in os.listdir(path):
        if (test_info in file) and file.endswith('.csv'):
            print(path+'\\'+file)
            df = pd.read_csv(path+'\\'+file,sep=';',skiprows=4)
            df['group']=file.rstrip('.csv')
            df_tot = df_tot.append(df,ignore_index=True)
    #df_tot.reset_index(inplace=True)
    df_tot
    chk = True
    print('Excel file to be generated ..'+final_file)
    if os.path.isfile(final_file):
        chk = f_input("Excel File already exists, want a new ?",output='str',choice=['y','n']) == 'y'
    if chk:
        df_tot.to_excel(final_file)
        print("excel file create ...")
        generate_score(path,test_info,dest_file)
    return df_tot
    
def generate_score(path='T:',test_info='TP01',dest_file='evalfinal_'):
    init_file = path+'\\'+dest_file+test_info+'.xlsx'
    final_file = path+'\\'+dest_file+test_info+'.txt'
    df = pd.read_excel(init_file)
    groups = set(df['group'].tolist())
    chk = True
    if os.path.isfile(final_file):
        chk = f_input("Txt File already exists, want a new ?",output='str',choice=['y','n']) == 'y'
    if chk:
        f = open(final_file, 'w')  # open file in append mode
    else:
        print("cancel ...")
        return None
    df.sort_values(by=['question','time'],inplace=True)

    for gr in groups:
        f.write("*"*80+'\n'+gr.rstrip('.csv')+'\n'*3) 
        t = PrettyTable()
        t.add_column('question',df.loc[df['group']==gr]['question'].values)
        t.add_column('time',df.loc[df['group']==gr]['time'].values)
        t.add_column('result',df.loc[df['group']==gr]['result'].values)
        t.add_column('attempt',df.loc[df['group']==gr]['attempt'].values)
        f.write(t.get_string())
        f.write('\n'*3)
    f.close()