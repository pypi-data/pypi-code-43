# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 18:26:31 2019

@author: u325199
"""

__version__ = "0.0.1"

import pandas as pd

def summary(df):
    unq = pd.DataFrame(df.nunique())
    unq["columns"] = unq.index
    unq.columns = ["UniqueValues","Columns"]
    unq = unq.reset_index(drop = True)

    cnt = df.count()
    cnt = pd.DataFrame(df.count())
    cnt["columns"] = cnt.index
    cnt.columns = ["TotalCount","Columns"]
    cnt = cnt.reset_index(drop = True)

    sum1 = df.describe().transpose()
    sum1["Columns"] = sum1.index

    m1 = pd.merge(cnt,unq)
    m1 = m1[m1.columns[[1,0,2]]]
    m2 = pd.merge(m1, sum1, how = "left")
    
    corrsheet = df.corr()
    
# Create a Pandas Excel writer using XlsxWriter as the engine.
    output = pd.ExcelWriter('Summarytest1.xlsx', engine='xlsxwriter')

# Write each dataframe to a different worksheet.
    m2.to_excel(output, sheet_name='Summary', index = False)
    corrsheet.to_excel(output, sheet_name='Correlation')    
# Close the Pandas Excel writer and output the Excel file.
    output.save()
    
