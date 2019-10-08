import time
import pandas as pd
import subprocess
import tempfile
import shutil
import os

def getAddress(share_x):
    # Pre-Check
    if 'Address1' not in share_x.columns:
        raise ValueError("Address1 column must be provided")
    elif 'City' not in share_x.columns:
        raise ValueError("City column must be provided")
    elif 'State' not in share_x.columns:
        raise ValueError("State column must be provided")
    elif 'Zipcode' not in share_x.columns:
        raise ValueError("Zipcode column must be provided")
    elif 'RowID' in share_x.columns:
        raise ValueError("RowID column name cannot be in dataframe")

    # Add Row ID
    share_x['RowID'] = share_x.index

    if 'Address2' not in share_x.columns:
        share_x['Address2'] = ""
 
    if 'Province' not in share_x.columns:
        share_x['Province'] = ""

    if 'Country' not in share_x.columns:
        share_x['Country'] = ""

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
    JarPath = os.path.dirname(PyShare.__file__) + "\share3.jar"

    subprocess.call(['java', '-cp', JarPath, 'com.fedex.share.example.ws.Option1ShareConnection', output_file, input_file])

    JavaReturn = pd.read_csv(output_file, sep="|")

    share_y = pd.merge(share_x, JavaReturn, on='RowID', how='left')

    # Cleanup
    del share_x['RowID']

    # Delete Temp Directory
    shutil.rmtree(temp_dir.name)

    return share_y
