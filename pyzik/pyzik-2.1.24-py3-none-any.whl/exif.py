# -*- coding: utf-8 -*-
"""
Created on Fri Jul 19 21:23:15 2019

@author: jazzn
"""

#from time import sleep
#import numpy as np
import pandas as pd
from requests import get
import pip
import os
import json
import PIL.Image,PIL.ExifTags


def install_pack(*package,proxy=None,option=None):
    print(f"version pip={pip.__version__}")
    if int(pip.__version__.split('.')[0])>9:
        from pip._internal import main
    else:
        from pip import main
    for p in package:
        print(f"\n********************** installation de {p} *************\n")
        if (proxy == None):
            if (option==None):
                try:
                    main(['install', p])
                except:
                    print(f">>> non installé")
            elif (option in ['pb','PB','PBayle','pbayle']):
                try:
                    main(['install','--proxy==192.168.224.254:3128', p])
                except:
                    print(f">>> non installé")
        else:
            try:
                main(['install',f'--proxy=={proxy}', p])
            except:
                print(f">>> non installé")
def get_exif_data(filename):
    img = PIL.Image.open(filename)
    exif = {PIL.ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in PIL.ExifTags.TAGS}
    for key in exif['GPSInfo'].keys():
        decode = PIL.ExifTags.GPSTAGS.get(key,key)
        exif[decode] = exif['GPSInfo'][key]
    del exif['GPSInfo']
    lat = exif['GPSLatitude']
    lon = exif['GPSLongitude']
    #sign = -1. if exif['GPSLongitudeRef'] == 'W' else 1.
    exif['GPSLatitude'] = {}
    exif['GPSLongitude'] = {}
    exif['GPSLatitude']["deg"] = lat[0][0]/lat[0][1]
    exif['GPSLatitude']["min"] = lat[1][0]/lat[1][1]
    exif['GPSLatitude']["sec"] = lat[2][0]/lat[2][1]
    exif['GPSLongitude']["deg"] = lon[0][0]/lon[0][1]
    exif['GPSLongitude']["min"] = lon[1][0]/lon[1][1]
    exif['GPSLongitude']["sec"] = lon[2][0]/lon[2][1]
    return exif
    
def trace2df(filename):
    """
    permet de transformer un tracert en dataframe contenant hop-RTT1-RTT2-RTT3-IP-lon-lat
    filename: fichier tracert
    La fonction utilise le service ipapi.co (site de géolocalisation des IP)
    Exemple:
        on fait un tracert de www.google.com comme ceci:
        tracert google.com >trace.txt
        (sur jupyter on utilise !)
        Ensuite 
        df = trace2df("trace.txt")
    """
    def corrected_line(line):
        p0 = line.rfind('ms ')+4
        p1 = line.find('[')+1
        p2 = line.find(']')
        name_of_server =line[p0:p1-1]
        line0 = line[:p0]+line[p1:p2]+'\n'
        return line0,name_of_server
    server_names =[]
    with open(filename, "r") as inpt:
        with open("__"+filename, "w") as output:
            output.write("hop     RTT1 ms1     RTT2 ms2     RTT3 ms3  IP\n")
            for line in inpt:
                if ' ms ' in line:
                    server_name="..."
                    if '[' in line:
                        line,server_name = corrected_line(line)
                    output.write(line)
                    server_names.append(server_name)
    filename = '__'+filename
    tr = pd.read_csv(filename,delim_whitespace=True)
    print("initial dataframe\n",tr)
    tr.drop(columns=['ms1','ms2','ms3'],inplace=True)
    tr['hop'] = pd.to_numeric(tr['hop'])
    tr['RTT1'] = pd.to_numeric(tr['RTT1'])
    tr['RTT2'] = pd.to_numeric(tr['RTT2'])
    tr['RTT3'] = pd.to_numeric(tr['RTT3'])
    tr['IP'] = tr['IP'].astype(str)
    tr['server_names'] = server_names
    print("\nMofification / removal of unnecessary columns")
    print("public IP search...",end='')
    try:
        ip = get('https://api.ipify.org').text
        print(ip)
        tr.at[0,'IP'] = ip
    except:
        print("unable to detect ur public ip")
    tr.drop_duplicates(subset=['IP'], keep='last',inplace=True)
    print("Elimination of duplicates\n")
    lons,lats,notes=[],[],[]
    print("IP Géolocation ... \n")
    for i,ip in enumerate(tr['IP']):
        try:
            detail = json.loads(get(f'https://ipapi.co/{ip}/json/').text)
            lon,lat,note = float(detail['longitude']),float(detail['latitude']),'...'
            if (lon == None) or (lat == None):
                lon = 0
                lat = 0
                note = f'unable [{i}]'
            lons.append(lon)
            lats.append(lat)
            notes.append(note)
        except:
            print(f"unable to geolocate ip={ip} - maybe private ip")
            lons.append(0)
            lats.append(0)
            notes.append(f'private IP [{i}]')
    tr['Latitude'] = lats
    tr['Longitude'] = lons
    tr['Note'] = notes
    tr.drop_duplicates(subset=['Latitude','Longitude','Note'], keep='last',inplace=True)
    print("Elimination of duplicates\n")
    os.remove(filename)
    print("***************** Finish")
    return tr    