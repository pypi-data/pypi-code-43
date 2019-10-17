import time
import pandas as pd
import subprocess
import tempfile
import shutil
import os
import PyShare
import datetime
from datetime import datetime, datetime as datetime_, timedelta

def getAddress(share_x,zip_len=5,return_cols=['Address','BusiResi','LatLon']):
    # Pre-Check
    start_time = datetime.now()
    share_x=share_x.copy()
    if 'Address1' not in share_x.columns:
        raise ValueError("Address1 column must be provided")
    elif 'RowID' in share_x.columns:
        del share_x['RowID']

    # Add Row ID
    share_x['RowID'] = share_x.index

    if 'Address2' not in share_x.columns:
        add2=False
        share_x['Address2'] = ""
    else:
        add2=True
 
    if 'Province' not in share_x.columns:
        prov=False
        share_x['Province'] = ""
    else:
        prov=True

    if 'Country' not in share_x.columns:
        country=False
        share_x['Country'] = ""
    else:
        country=True

    if 'City' not in share_x.columns:
        city=False
        share_x['City'] = ""
    else:
        city=True
 
    if 'State' not in share_x.columns:
        state=False
        share_x['State'] = ""
    else:
        state=True

    if 'Zipcode' not in share_x.columns:
        zipcode=False
        share_x['Zipcode'] = ""
    else:
        zipcode=True

    # Create Dataframe to Send to Java
    JavaDF = share_x[['Address1','Address2','City','State','Zipcode','Province','Country','RowID']]

    # Create Temp Directory
    temp_dir = tempfile.TemporaryDirectory()

    file_name = int(time.time())

    # Set Input and Output
    input_file = '{}\{}.txt'.format(temp_dir.name,file_name)
    output_file = '{}\{}_complete.txt'.format(temp_dir.name,file_name)

    JavaDF.to_csv(input_file, header=True, index=False, sep='|')

    # Get Jar Path
    JarPath = os.path.dirname(PyShare.__file__) + "\sharedev.jar"

    FNULL = open(os.devnull, 'w')
    subprocess.call(['java', '-cp', JarPath, 'com.fedex.share.example.ws.Option1ShareConnection', 'File', output_file, input_file], stdout=FNULL, stderr=subprocess.STDOUT)

    JavaReturn = pd.read_csv(output_file, sep="|")

    if len(JavaReturn) == 0:
        raise ValueError("Share Service Down")

    share_x = pd.merge(share_x, JavaReturn, on='RowID', how='left')

    # Set Zipcode Output Length
    if zip_len == 5:
        share_x['Std_Zipcode'] = share_x['Std_Zipcode'].str[:5]

    # Set Output Columns
    if 'Address' not in return_cols:
        share_x.drop(['Std_Address1', 'Std_Address2', 'Std_City', 'Std_State', 'Std_Zipcode', 'Std_Country', 'MultiUnitBase', 'AddressPrecision'], axis=1, inplace=True)

    if 'BusiResi' not in return_cols:
        del share_x['Busi_Resi']

    if 'LatLon' not in return_cols:
        share_x.drop(['GeoLatitude', 'GeoLongitude', 'Rank'], axis=1, inplace=True)

    # Row Cleanup of Source
    del share_x['RowID']

    if add2 == False:
        del share_x['Address2']
    if prov == False:
        del share_x['Province']
    if country == False:
        del share_x['Country']
    if city == False:
        del share_x['City']
    if state == False:
        del share_x['State']
    if zipcode == False:
        del share_x['Zipcode']

    end_time = datetime.now()

    t = end_time - start_time
    print("*** Speed:", t.seconds/len(share_x), "seconds per call ***")
    print('*** Share returned', len(JavaReturn), 'of',len(share_x),'requested records ***')
    return share_x



def getShare(share_x,zip_len=5,return_cols=['Address','BusiResi','LatLon']):
    # Pre-Check
    start_time = datetime.now()
    share_x=share_x.copy()
    if 'ShareID' not in share_x.columns:
        raise ValueError("ShareID column must be provided")
    elif 'RowID' in share_x.columns:
        del share_x['RowID']

    # Add Row ID
    share_x['RowID'] = share_x.index

    # Create Dataframe to Send to Java
    JavaDF = share_x[['ShareID','RowID']]

    # Create Temp Directory
    temp_dir = tempfile.TemporaryDirectory()

    file_name = int(time.time())

    # Set Input and Output
    input_file = '{}\{}.txt'.format(temp_dir.name,file_name)
    output_file = '{}\{}_complete.txt'.format(temp_dir.name,file_name)

    JavaDF.to_csv(input_file, header=True, index=False, sep='|')

    # Get Jar Path
    JarPath = os.path.dirname(PyShare.__file__) + "\sharedev.jar"

    FNULL = open(os.devnull, 'w')
    subprocess.call(['java', '-cp', JarPath, 'com.fedex.share.example.ws.Option1ShareConnection', 'File', output_file, input_file], stdout=FNULL, stderr=subprocess.STDOUT)

    JavaReturn = pd.read_csv(output_file, sep="|")

    if len(JavaReturn) == 0:
        raise ValueError("Share Service Down")

    share_x = pd.merge(share_x, JavaReturn, on='RowID', how='left')

    # Set Zipcode Output Length
    if zip_len == 5:
        share_x['Std_Zipcode'] = share_x['Std_Zipcode'].str[:5]

    # Set Output Columns
    if 'Address' not in return_cols:
        share_x.drop(['Std_Address1', 'Std_Address2', 'Std_City', 'Std_State', 'Std_Zipcode', 'Std_Country', 'MultiUnitBase', 'AddressPrecision'], axis=1, inplace=True)

    if 'BusiResi' not in return_cols:
        del share_x['Busi_Resi']

    if 'LatLon' not in return_cols:
        share_x.drop(['GeoLatitude', 'GeoLongitude', 'Rank'], axis=1, inplace=True)

    # Row Cleanup of Source
    del share_x['RowID']

    end_time = datetime.now()

    t = end_time - start_time
    print("*** Speed:", t.seconds/len(share_x), "seconds per call ***")
    print('*** Share returned', len(JavaReturn), 'of',len(share_x),'requested records ***')
    return share_x
