import pandas as pd
import numpy as np
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import matplotlib.pyplot as plt

global df

def get_data():
    global df
    df = pd.read_csv('data\\fishcolors.csv')

def get_fish():
    global df
    all_options = df.option.unique()
    return all_options

def hex_to_rgba(hex, alpha = 1.):
     hex = hex.lstrip('#')
     hlen = len(hex)
     return tuple([int(hex[i:i+hlen//3], 16)/255 for i in range(0, hlen, hlen//3)] + [alpha])

def make_cdict(color_array):
    cdict_names = ['red', 'green', 'blue']
    cdict = {}

    colors = np.array([hex_to_rgba(cl) for cl in color_array])
    for cl in range(3):
        new_col = np.concatenate((np.expand_dims(np.linspace(0,1,colors.shape[0]),axis=1),np.expand_dims(colors[:,cl], axis=1),
                          np.expand_dims(colors[:,cl], axis=1)), axis=1)
        cdict[cdict_names[cl]] = new_col
    return cdict

def fish(n_colors = 8, option = 'Hypsypops_rubicundus'):
    if not option in get_fish():
        raise Exception('That fish is not in the database, please check your spelling and try again')

    color_array = np.array(df[df.option == option].hex)
    cdict = make_cdict(color_array)
    newcmp = LinearSegmentedColormap('testCmap', segmentdata=cdict, N=256)
    return newcmp
