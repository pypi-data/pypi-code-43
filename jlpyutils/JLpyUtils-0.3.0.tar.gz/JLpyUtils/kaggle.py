"""
This module contains functions for interacting with kaggle.
"""
import json as _json
import os as _os

def setup_config_dir(username, key):
    
    """
    Setup a kaggle.json file with the necessary configuration credentials in the kaggle api directory
    
    Arguments:
    ----------
        username: kaggle username
        key: key contained in the json file from `https://www.kaggle.com/<username>/account`
    
    Returns:
    --------
        None. creates a kaggle.json file in the kaggle api directory.
    """

    config_dir = _os.path.join(_os.path.expanduser('~'),'.kaggle')
    if _os.path.isdir(config_dir)==False:
        _os.makedirs(config_dir)

    config_dict = {"username":username,
                   "key": key}

    file = open(_os.path.join(config_dir,'kaggle.json'),'w')
    _json.dump(config_dict, file)
    file.close()

def competition_download_files(competition, 
                               path_report_dir = '.',
                               verbose = 1):
    """
    download competition files for the 'competition' ID (string) passed
    
    Arguments:
    ----------
        competition: kaggle competition ID. If you unsure of the exact ID, just pass '' and an error will be raised with a list of valid competitions
        path_report_dir: the directory where the data will be stored in a sub-directory with the name of the competition.
        verbose: print-out verbosity
        
    Returns:
    --------
        None. The competition files will be saved in a sub-directory with the competition name/ID within the path_report_dir
    """
    from kaggle.api.kaggle_api_extended import KaggleApi
    import sys, os, zipfile
    
    api = KaggleApi()
    api.authenticate()
    
    competitions = [str(comp) for comp in api.competitions_list()]
    
    assert(competition in competitions), str(competition)+' is not a valid competition. Valid competitions include:\n'+'\n'.join(competitions)
    
    path_competition = _os.path.join(path_report_dir,competition)
    files = api.competition_download_files(competition, 
                                           path = path_competition)

    #unzip files
    for file in os.listdir(path_competition):
        if 'zip' in file:
            with zipfile.ZipFile(os.path.join(path_competition, file) , 'r') as zip_ref:
                zip_ref.extractall(path_competition)
            os.remove(os.path.join(path_competition, file))
    
    if verbose>=1:
        print('competition files:')
        for file in os.listdir(path_competition):
            print(file, '\t',round(os.path.getsize(os.path.join(path_competition, file))*10**-6,2),'Mb')