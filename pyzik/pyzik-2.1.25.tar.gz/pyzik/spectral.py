# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 05:12:01 2019

@author: jittima
"""

import os
from IPython.display import Image
import wget
from cirpy import resolve
from jcamp import JCAMP_reader
import pandas as pd
import requests
from astroquery.nist import Nist
import astropy.units as u
from bs4 import BeautifulSoup 

def get_jdx(nistid, stype='IR',index = 0):
    """Download jdx file for the specified NIST ID, unless already downloaded."""
    NIST_URL = 'http://webbook.nist.gov/cgi/cbook.cgi'
    filepath = os.path.join(f'{nistid}-{stype}.jdx')
    if os.path.isfile(filepath):
        print(f'{nistid} {stype}: Already exists at {filepath}')
        return
    print(f'{nistid} {stype}: Downloading')
    response = requests.get(NIST_URL, params={'JCAMP': nistid, 'Type': stype, 'Index': index})
    with open(filepath, 'w') as file:
        file.write(response.text)
    return filepath


def get_prefered_phase_index(nistid,stype='IR-SPEC',prefered_phase = 'SOLUTION',final_index=0):
    #prefered_phase = 'GAZ' or 'LIQUID'
    NIST_URL = 'http://webbook.nist.gov/cgi/cbook.cgi'
    if stype=='IR':
        stype = 'IR-SPEC'
    #https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C71363&Index=1&Type=IR
    #r = requests.get("https://webbook.nist.gov/cgi/cbook.cgi?ID=C71363&Type=IR-SPEC&Index=1#IR-SPEC")
    kw0 = ['Owner','Origin','Source reference','Date']
    kw1 = ['Instrument','Resolution','Instrument parameters','Data processing']
    for index in [3,2,1]:
        idx = str(index)+'#'+stype
        response = requests.get(NIST_URL, params={'ID': nistid, 'Type': stype, 'Index': idx})
        if 'IR Spectrum' not in response.text:
            continue
        else:
            soup = BeautifulSoup(response.text,'html.parser')
            for kw in kw0:
                try:
                    i0 = soup.get_text().index(kw)
                    break
                except:
                    i0 = 0
                    pass
            for kw in kw1:
                try:
                    i1 = soup.get_text().index(kw)
                    break
                except:
                    i1 = len(soup.get_text())
                    pass
            l = soup.get_text()[i0:i1].split('\n')
            indice = 0
            if 'State' in l:
                for i,elem in enumerate(l):
                    if elem == 'State':
                        indice = i+1
                        break
            if prefered_phase in l[indice]:
                print(f'prefered phase={prefered_phase}/{index} found')
                return index
            else:
                print(f'prefered phase={prefered_phase}/{index} not found')
    return final_index
        
def get_cas(name):
    result = resolve(name,'cas')
    if result == None:
        print('nothing find, name of molecule must be Systematic IUPAC name')
        return 
    else:
        if isinstance(result,list):
            nb_char = 99999
            cas_name = ''
            for cas in result:
                if len(cas)<nb_char:
                    nb_char = len(cas)
                    cas_name = cas
            return cas_name
        else:        
            return result

def add_cols(df): #df est une dataframe spectrale
    if 'TRANSMITTANCE' not in df.columns:   #commenter cette ligne
        df['TRANSMITTANCE'] = df.eval('10**(-ABSORBANCE)')
    if '1/CM' not in df.columns: #commenter cette ligne
        df['1/CM'] = df.eval('10000/MICROMETER')
    return df

def get_spectrum(cas,spectrum_type='IR',prefered_phase='SOLUTION (10%',forced_index=(False,0),have_cols=False):
    #other type : 'UVVis'
    if spectrum_type != 'IR':
        spectrum_type = 'UVVis'
    cas0 = cas.replace('-','')
    nist = 'C'+cas0
    if spectrum_type == 'IR':
        index = get_prefered_phase_index(nist,stype=spectrum_type,prefered_phase=prefered_phase,final_index=forced_index[1]) if not forced_index[0] else forced_index[1]
    else:
        index = 0
    namefile = get_jdx(nist,stype=spectrum_type,index=index)
    if namefile == None:
        return 
    jcamp_dict = JCAMP_reader(namefile)
    if not 'xunits' in jcamp_dict:
        os.remove(namefile)
        print(f"\nresolve cas = {cas} failled")
        return
    result = pd.DataFrame({jcamp_dict['xunits']:jcamp_dict['x'],jcamp_dict['yunits']:jcamp_dict['y']})
    result.info = f'IR|{cas}'
    if have_cols:
        result = add_cols(result)
    z = os.path.getsize(namefile)
    os.remove(namefile)
    if z>1024:
        print('index = ',index)
        print(f"\n{80*'='}\ncas={cas}\ncolumns names={result.columns}\n{80*'='}")
        return result
    else:
        print(f"\nresolve cas = {cas} failled")
        return

def mol_display(cas):
    cas0 = 'C'+cas.replace('-','')
    name=f"Dcas{cas0}.jpg"
    url = f"https://webbook.nist.gov/cgi/cbook.cgi"
    params={'Struct':cas0,'Type':'Color'}
    urlf = requests.get(url=url,params=params).url
    wget.download(urlf,name)
    z = os.path.getsize(name)
    if z>1024:
        return Image(name)
        os.remove(name)
    else:
        print(f"resolve cas = {cas} failled")
        os.remove(name)
        return

def get_element_spectrum(element,lower=400,upper=800,definition=0.01,rel_min=2):
    element = element.strip()
    if ' ' not in element:
        element += ' I'
    table = Nist.query(lower*u.nm,upper*u.nm,linename=element)
    A = pd.DataFrame({'lamb':table['Observed'],'rel':table['Rel.']})
    A['rel']=pd.to_numeric(A['rel'], errors='coerce')
    A.dropna(inplace=True)
    A['rel'] = A['rel'].astype(float)
    A['rel']=A['rel']*100/A['rel'].max()
    A.drop_duplicates(inplace=True)
    A['Dl']=A['lamb'].shift(-1)-A['lamb']
    A['Dl'].fillna(definition*1.1,inplace=True)
    A = A[A['Dl']>definition]
    A.drop(columns=['Dl'],inplace=True)
    A = A[A['rel']>rel_min]
    A.reset_index(inplace=True)
    A.drop(columns=['index'],inplace=True)
    A.info = f"spectrum: {element}"
    return A