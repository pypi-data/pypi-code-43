#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage: 
#    ./a3cosmos_cutouts_make_cutouts_for_input_images_by_RA_Dec.py -image image1.fits image2.fits -ra XXX -dec XXX -FoV XXX
#

import os, sys, re, json, copy, datetime, time
import numpy as np
import astropy
#from astropy.table import Table
#from astropy.io import fits
#from astropy import units as u
#from astropy import wcs
#from astropy.wcs import WCS
#from astropy.wcs.utils import proj_plane_pixel_scales
#from astropy.coordinates import SkyCoord, FK5
#import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL import (generate_query_dict, query_cosmos_cutouts_via_IRSA_HTTP_URL)


# 
# def make_cutout
# 
def make_cutout(RA = np.nan, Dec = np.nan, FoV = np.nan, Band = '', Field = '', OutputFolder = ''):
    # 
    if np.isnan(RA) or np.isnan(Dec) or np.isnan(FoV) or Band == '':
        raise Exception('Error! Wrong input to make_cutout! Please check RA = %s, Dec = %s, FoV = %s, Band = \'%s\', Field = \'%s\', OutputFolder = \'%s\'!'%(RA, Dec, FoV, Band, Field, OutputFolder))
    # 
    Source_Coordinate_Box = generate_query_dict()
    Source_Coordinate_Box['RA'] = RA
    Source_Coordinate_Box['Dec'] = Dec
    Source_Coordinate_Box['FoV'] = FoV
    # 
    if Field == '':
        Cutout_Field = 'COSMOS'
    elif re.match('COSMOS', Field, re.IGNORECASE):
        Cutout_Field = 'COSMOS'
    elif re.match('COSMOS_INT', Field, re.IGNORECASE):
        Cutout_Field = 'COSMOS_INT'
        if os.getenv('Http_User_Name') is None or os.getenv('Http_User_Pass') is None:
            raise Exception('Error! Wrong input to make_cutout! Field = \'%s\' but environment variable \"$Http_User_Name\" and \"$Http_User_Pass\" do not exist!'%(Field))
    else:
        raise Exception('Error! Wrong input to make_cutout! Field = \'%s\' is not acceptable!'%(Field))
    # 
    if Cutout_Field == 'COSMOS' and re.match('(UVISTA_|)(K|Ks)', Band, re.IGNORECASE):
        Cutout_Band = ['UVISTA_K']
    if Cutout_Field == 'COSMOS' and re.match('(UVISTA_|)(H)', Band, re.IGNORECASE):
        Cutout_Band = ['UVISTA_H']
    if Cutout_Field == 'COSMOS' and re.match('(UVISTA_|)(J)', Band, re.IGNORECASE):
        Cutout_Band = ['UVISTA_J']
    if Cutout_Field == 'COSMOS' and re.match('(ACS_|)(i|F814W)', Band, re.IGNORECASE):
        Cutout_Band = ['ACS_F814W']
    if Cutout_Field == 'COSMOS' and re.match('(VLA_|)(3GHz|10cm)', Band, re.IGNORECASE):
        Cutout_Band = ['VLA_3GHz']
    else:
        raise Exception('Error! Wrong input to make_cutout! Field = \'%s\' and Band = \'%s\' is not acceptable!'%(Field, Band))
    # 
    Http_User_Name = ''
    Http_User_Pass = ''
    Overwrite_Level = 0
    if OutputFolder == '':
        Output_Folder = 'a3cosmos_cutouts'
    # 
    query_cosmos_cutouts_via_IRSA_HTTP_URL(Source_Coordinate_Box, \
                                           Cutout_Field, \
                                           Cutout_Band, \
                                           Output_Folder = Output_Folder, \
                                           Http_User_Name = Http_User_Name, \
                                           Http_User_Pass = Http_User_Pass, \
                                           Overwrite_Level = Overwrite_Level )
    # 
    # 









