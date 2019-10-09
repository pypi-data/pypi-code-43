import pandas as pd
import numpy as np
import load_data
import sys, os


def herfindahl_index(metrics_data):
    '''
    returns local and nonlocal functional markers based on herfindahl index cutoff
    '''
    fms = pd.DataFrame()
    for f in set(metrics_data["FM"]):
        fm = metrics_data[metrics_data["FM"]==f]
        p = fm["ESTAB"]/fm['ESTAB'].sum()
        h = (p**2).sum()
        fms = fms.append([[f, h]])
    fms.columns= ['FM', 'Herfindahl Index']
    local = sorted(list(fms[fms['Herfindahl Index'] <= 0.02]['FM']))
    non_local =  sorted(list(fms[fms['Herfindahl Index'] > 0.02]['FM']))
    return (local, non_local)


def presence_metric(metrics_data):
    '''
    returns local and nonlocal functional markers based on presence metric > 1 in micropolitan data cutoff
    '''
    local = ['transmission','real estate','real estate construction and subcontractors',
                'manufacturing','social & advocacy organizations',
                'real estate components and materials','financial services',
                'fuel retails and wholesales','energy retails and wholesales',
                'apparel and jewelry retail','real estate lessor','leisure activities','fueling',
                'finished goods manufacturing','consumer services','grocery stores','transportation',
                'banks and lending','insurance','maintenance and repair','food services','gas stations',
                'restaurants and restaurant services','retail','energy',
                'retail, wholesale, distribution','telecommunications','business services',
                'real estate components and materials sales','government',
                'finance, accounting, and notaries','bars and restaurants',
                'commercial and industrial products wholesalers','restaurants','real estate operators',
                'diversified shipping','food','vehicles','equipment wholesale and distribution',
                'healthcare services','healthcare providers','financial information','public services',
                'shipping','media','transportation of goods','vehicle, vehicle parts, and fuel retail',
                'tourism and leisure','finance and banking','healthcare','ground shipping',
                'accounting and taxes','food and drink retail','automobiles and motorcyles',
                'diversified equipment retail','vehicle parts stores','wholesale and distribution',
                'consumer banks and lenders','commercial banks and lenders','real estate construction',
                'shipping and temporary storage','contractors and installers','caretaking',
                'home improvement retail','real estate services','restaurants and food trucks','sale',
                'restaurants and grocery','infrastructure', 'vehicle dealerships']
    fm_list = sorted(list(set(metrics_data["FM"])))
    non_local = sorted(list(set(LOCAL_FMS) ^ set(fm_list)))
    return (local, non_local)

def mutually_exclusive():
    '''
    returns functional markers that the FM team came up with and we determined to be mostly mutually exclusive
    '''
    MUTUALLY_EXCLUSIVE = ['agriculture, fishing, and forestry', 'real estate', 
                          'real estate construction', 'real estate components and materials',
                          'real estate lessor', 'public services', 'mining', 'extraction', 'media', 
                          'tv and movies', 'music', 'manufacturing', 'finished goods manufacturing', 
                          'components manufacturing', 'material manufacturing', 'transportation', 
                          'electricity','telecommunications', 'pipelines', 
                          'water and sewage systems', 'utility equipment and services', 
                          'gas utilities', 'healthcare', 'pharmaceuticals and biotech', 
                          'food processing and manufacturing', 'energy', 'finance and banking', 
                          'airplanes', 'trains', 'boats', 'transportation of people', 'transportation of goods', 
                          'food services', 'entertainment establishments','tourism', 'technology', 
                          'hardware', 'software', 'retail', 'wholesale and distribution', 'consumer services', 
                          'business services']
    return MUTUALLY_EXCLUSIVE



if __name__ == '__main__':
    os.chdir("../../peer-explorer")
    metrics_data = pd.read_csv("data/processed/metrics.csv")
    metrics_data = metrics_data[metrics_data["YEAR"]==2016]
    
                     
    
    
    
    