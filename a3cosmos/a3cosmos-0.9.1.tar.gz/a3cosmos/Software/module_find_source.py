#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage: 
#    ./a3cosmos_cutouts_make_cutouts_for_input_images_by_RA_Dec.py -image image1.fits image2.fits -ra XXX -dec XXX -FoV XXX
#

import os, sys, re, json, copy, datetime, time, shutil
import numpy as np
import astropy
from astropy.table import Table
#from astropy.io import fits
#from astropy import units as u
#from astropy import wcs
#from astropy.wcs import WCS
#from astropy.wcs.utils import proj_plane_pixel_scales
#from astropy.coordinates import SkyCoord, FK5
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

#from a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL import (generate_query_dict, query_cosmos_cutouts_via_IRSA_HTTP_URL)



# 
# 
# 
def master_catalog():
    raise NotImplementedError('Oops, A3COSMOS master catalog is too large to be distributed with this code. Please contact a3cosmos team https://sites.google.com/view/a3cosmos!')
    return os.path.dirname(os.path.abspath(__file__))

def data_version():
    #return '20180102'
    return '20180801'

def prior_catalog():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Data', data_version())
    file_list = os.listdir(data_dir)
    for file_name in file_list:
        if re.match(r'^A-COSMOS_prior_.*.fits', file_name, re.IGNORECASE):
            return os.path.join(data_dir, file_name)
    raise Exception('Error! Could not find "A-COSMOS_prior_*.fits" under "%s"! List of files: %s'%(data_dir, file_list))

def blind_catalog():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Data', data_version())
    file_list = os.listdir(data_dir)
    for file_name in file_list:
        if re.match(r'^A-COSMOS_blind_.*.fits', file_name, re.IGNORECASE):
            return os.path.join(data_dir, file_name)
    raise Exception('Error! Could not find "A-COSMOS_blind_*.fits" under "%s"! List of files: %s'%(data_dir, file_list))

def read_prior_catalog():
    #print('Reading "%s"'%(prior_catalog()))
    catalog = Table.read(prior_catalog(), format='fits')
    #<TODO># homogenize
    if 'DEC' in catalog.colnames and not ('Dec' in catalog.colnames):
        catalog.rename_column('DEC', 'Dec')
    return catalog

def read_blind_catalog():
    #print('Reading "%s"'%(blind_catalog()))
    catalog = Table.read(blind_catalog(), format='fits')
    #<TODO># homogenize
    if 'DEC' in catalog.colnames and not ('Dec' in catalog.colnames):
        catalog.rename_column('DEC', 'Dec')
    return catalog


# 
# def query_a3cosmos_galfit_catalog_by_ID_Master
# 
#def query_a3cosmos_galfit_catalog_by_ID_Master(ID_Master, output_columns = [], output_flat_array = False):
#    global cat
#    if cat is None:
#        cat = Table.read()
#    found_items_for_all_columns = []
#    for output_column in output_columns:
#        found_items = []
#        if output_column in cat.colnames:
#            cat_indexes = np.argwhere(cat['ID']==ID_Master).flatten()
#            for cat_index in cat_indexes:
#                found_items.append(cat[output_column][cat_index])
#        if not output_flat_array:
#            found_items_for_all_columns.append(found_items)
#        else:
#            found_items_for_all_columns.extend(found_items)
#    return found_items_for_all_columns



# 
# def print_catalog_rows
# 
def print_found_catalog_rows(catalog, finding_method, found_indices, recording_file = None):
    for i, found_index in enumerate(found_indices):
        RA = catalog['RA'][found_index]
        Dec = catalog['Dec'][found_index]
        flux = catalog['Total_flux_pbcor'][found_index]
        flux_err = catalog['E_Total_flux_pbcor'][found_index]
        wavelength = catalog['Obs_wavelength'][found_index]
        image_file = catalog['Image_file'][found_index].strip()
        printing_str = 'Found source with %s at row %d, RA Dec %.8f %.8f, flux %s ± %s [mJy], wavelength %s [um], image_file \"%s\"'%(finding_method, found_index+1, RA, Dec, flux, flux_err, wavelength, image_file)
        print(printing_str)
        if recording_file is not None:
            recording_file.write(printing_str+'\n')
            recording_file.flush()



# 
# def find_source
# 
def find_source(RA = np.nan, Dec = np.nan, ID = -1, sep = 1.5):
    # 
    #if type(RA) is str or type(Dec) is str:
    #    TODO
    # 
    if (np.isnan(RA) or np.isnan(Dec)) and (ID < 0):
        raise Exception('Error! Wrong input to make_cutout! Please check RA = %s, Dec = %s, ID = %s!'%(RA, Dec, ID))
    # 
    # check 'a3cosmos_find_source_log.txt'
    if os.path.isfile('a3cosmos_find_source_in_prior_catalog.log'):
        shutil.move('a3cosmos_find_source_in_prior_catalog.log', 'a3cosmos_find_source_in_prior_catalog.log.backup')
    if os.path.isfile('a3cosmos_find_source_in_blind_catalog.log'):
        shutil.move('a3cosmos_find_source_in_blind_catalog.log', 'a3cosmos_find_source_in_blind_catalog.log.backup')
    # 
    # if user has input ID, query prior catalog
    if ID >= 0:
        catalog = read_prior_catalog()
        finding_method = 'ID %d'%(ID)
        found_indices = np.argwhere(catalog['ID'] == ID)[0].tolist()
        if np.count_nonzero(found_indices) == 0:
            print('No source found in prior catalog with %s!'%(finding_method))
            return
        else:
            with open('a3cosmos_find_source_in_prior_catalog.log', 'w') as fp:
                print('Found %d sources in prior catalog with %s!'%(np.count_nonzero(found_indices), finding_method))
                print_found_catalog_rows(catalog, finding_method, found_indices, fp)
            print('Written to "%s"!'%('a3cosmos_find_source_in_prior_catalog.log'))
    # otherwise search by RA Dec in both catalogs
    else:
        catalog = read_prior_catalog()
        distances = np.sqrt(((catalog['RA'] - RA)*np.cos(np.deg2rad(Dec)))**2 + (catalog['Dec'] - Dec)**2)
        finding_method = 'RA Dec %.8f %.8f and search radius %.2f arcsec'%(RA, Dec, sep)
        found_indices = np.argwhere(distances <= sep/3600.0)[0].tolist()
        if np.count_nonzero(found_indices) == 0:
            print('No source found in prior catalog with %s!'%(finding_method))
        else:
            with open('a3cosmos_find_source_in_prior_catalog.log', 'w') as fp:
                print('Found %d sources in prior catalog with %s!'%(np.count_nonzero(found_indices), finding_method))
                print_found_catalog_rows(catalog, finding_method, found_indices, fp)
            print('Written to "%s"!'%('a3cosmos_find_source_in_prior_catalog.log'))
        # 
        catalog = read_blind_catalog()
        distances = np.sqrt(((catalog['RA'] - RA)*np.cos(np.deg2rad(Dec)))**2 + (catalog['Dec'] - Dec)**2)
        finding_method = 'RA Dec %.8f %.8f and search radius %.2f arcsec'%(RA, Dec, sep)
        found_indices = np.argwhere(distances <= sep/3600.0)[0].tolist()
        if np.count_nonzero(found_indices) == 0:
            print('No source found in blind catalog with %s!'%(finding_method))
        else:
            with open('a3cosmos_find_source_in_blind_catalog.log', 'w') as fp:
                print('Found %d sources in blind catalog with %s!'%(np.count_nonzero(found_indices), finding_method))
                print_found_catalog_rows(catalog, finding_method, found_indices, fp)
            print('Written to "%s"!'%('a3cosmos_find_source_in_blind_catalog.log'))
    # 
    # 







