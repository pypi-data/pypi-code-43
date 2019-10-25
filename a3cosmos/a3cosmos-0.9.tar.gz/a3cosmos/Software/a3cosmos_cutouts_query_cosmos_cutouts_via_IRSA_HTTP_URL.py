#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage: 
#    ./a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL.py
# 
# Note:
#    This code is copied from 'Github/AlmaCosmos/Softwares/almacosmos_cutouts_query_cosmos_cutouts_via_IRSA.py'
# 
# 

import os, sys, re, json, subprocess
import numpy
import astropy
from astropy.wcs import WCS
from astropy.nddata import Cutout2D
from astropy.io.fits import Header
from copy import copy
from pprint import pprint
from getpass import getpass
#import binascii
#from regions import DS9Parser, read_ds9, write_ds9

import six
bytes_to_hex_str = lambda bb: ''.join('%02x'%(tt) for tt in six.iterbytes(bb)).upper() # print bytes as hex
string_to_hex_str = lambda bb: ''.join('%02x'%(ord(tt)) for tt in six.iterbytes(bb)).upper() # print string as hex
def check_non_ascii(input_bytes):
    # check if a byte array contains non ascii char
    for input_char in input_bytes:
        #print('%02x'%(input_char))
        if input_char == 0 or input_char > 128:
            #print('%02x found in "%s"'%(input_char, input_bytes))
            return True
    return False

import requests
import requests_toolbelt # pip install --user requests-toolbelt
from requests_toolbelt.multipart.decoder import MultipartDecoder # https://pypi.org/project/requests-toolbelt/




# Initialize
def generate_query_dict():
    Source_Coordinate_Box = {
                                'ID': '', 
                                'RA': numpy.nan, 
                                'Dec': numpy.nan, 
                                'FoV': 15.0, 
                                'PX': numpy.nan, 
                                'PY': numpy.nan, 
                                'DX': numpy.nan, 
                                'DY': numpy.nan, 
                                'Cutout_LowerX': numpy.nan, 
                                'Cutout_LowerY': numpy.nan, 
                                'Cutout_UpperX': numpy.nan, 
                                'Cutout_UpperY': numpy.nan, 
                            }

    return Source_Coordinate_Box



# get_IRSA_image_url_dict
def get_IRSA_image_url_dict():
    Image_url_dict = {
                    'COSMOS_UVISTA_J':      'http://irsa.ipac.caltech.edu/data/COSMOS/images/Ultra-Vista/mosaics/COSMOS.J.UV_original_psf.v1.fits',  
                    'COSMOS_UVISTA_H':      'http://irsa.ipac.caltech.edu/data/COSMOS/images/Ultra-Vista/mosaics/COSMOS.H.UV_original_psf.v1.fits',  
                    'COSMOS_UVISTA_K':      'http://irsa.ipac.caltech.edu/data/COSMOS/images/Ultra-Vista/mosaics/COSMOS.K.UV_original_psf.v1.fits',  
                    'COSMOS_UVISTA_Y':      'http://irsa.ipac.caltech.edu/data/COSMOS/images/Ultra-Vista/mosaics/COSMOS.Y.UV_original_psf.v1.fits',  
                    'COSMOS_INT_UVISTA_Y':  'http://irsa.ipac.caltech.edu/data/COSMOS_INT/images/Ultra-Vista/COSMOS.Y.UV_original_psf.v3.sci.fits',  
                    'COSMOS_INT_UVISTA_J':  'http://irsa.ipac.caltech.edu/data/COSMOS_INT/images/Ultra-Vista/COSMOS.J.UV_original_psf.v3.sci.fits',  
                    'COSMOS_INT_UVISTA_H':  'http://irsa.ipac.caltech.edu/data/COSMOS_INT/images/Ultra-Vista/COSMOS.H.UV_original_psf.v3.sci.fits',  
                    'COSMOS_INT_UVISTA_K':  'http://irsa.ipac.caltech.edu/data/COSMOS_INT/images/Ultra-Vista/COSMOS.Ks.UV_original_psf.v3.sci.fits', 
                    'COSMOS_INT_IRAC_ch1':  'http://irsa.ipac.caltech.edu/data/COSMOS_INT/images/spitzer/splash/mosaics/all.irac.1.mosaic.fits', 
                    'COSMOS_INT_IRAC_ch2':  'http://irsa.ipac.caltech.edu/data/COSMOS_INT/images/spitzer/splash/mosaics/all.irac.2.mosaic.fits', 
                    'COSMOS_INT_IRAC_ch3':  'http://irsa.ipac.caltech.edu/data/COSMOS_INT/images/spitzer/splash/mosaics/all.irac.3.mosaic.fits', 
                    'COSMOS_INT_IRAC_ch4':  'http://irsa.ipac.caltech.edu/data/COSMOS_INT/images/spitzer/splash/mosaics/all.irac.4.mosaic.fits', 
                   #'COSMOS_ACS_i':         'http://irsa.ipac.caltech.edu/data/COSMOS/images/acs_mosaic_2.0/mosaic_Shrink10.fits',  
                   #'COSMOS_ACS_F814W':     'http://irsa.ipac.caltech.edu/data/COSMOS/images/acs_mosaic_2.0/mosaic_Shrink10.fits',  
                    'COSMOS_ACS_i':         'http://irsa.ipac.caltech.edu/data/COSMOS/images/acs_mosaic_2.0/acs_I_mosaic_30mas_sci.fits', 
                    'COSMOS_ACS_F814W':     'http://irsa.ipac.caltech.edu/data/COSMOS/images/acs_mosaic_2.0/acs_I_mosaic_30mas_sci.fits', 
                    'COSMOS_PACS_100':      'https://irsa.ipac.caltech.edu/data/COSMOS/images/herschel/pacs/pep_COSMOS_green_Map.DR1.sci.fits', 
                    'COSMOS_PACS_160':      'https://irsa.ipac.caltech.edu/data/COSMOS/images/herschel/pacs/pep_COSMOS_red_Map.DR1.sci.fits', 
                    'COSMOS_SPIRE_250':     'https://irsa.ipac.caltech.edu/data/COSMOS/images/herschel/spire/COSMOS-Nest_image_250_SMAP_v6.0.fits', 
                    'COSMOS_SPIRE_350':     'https://irsa.ipac.caltech.edu/data/COSMOS/images/herschel/spire/COSMOS-Nest_image_350_SMAP_v6.0.fits', 
                    'COSMOS_SPIRE_500':     'https://irsa.ipac.caltech.edu/data/COSMOS/images/herschel/spire/COSMOS-Nest_image_500_SMAP_v6.0.fits', 
                    'COSMOS_VLA_3GHz':      'https://irsa.ipac.caltech.edu/data/COSMOS/images/vla/vla_3ghz_msmf.fits', 
                }
    return Image_url_dict



# get_IRSA_image_header_cache_dict
def get_IRSA_image_header_cache_dict():
    Image_header_cache_dict = {
                   #'COSMOS_UVISTA_J':      os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_UVISTA_J.header',  
                   #'COSMOS_UVISTA_H':      os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_UVISTA_H.header',  
                    'COSMOS_UVISTA_K':      os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_UVISTA_K.header',  
                   #'COSMOS_UVISTA_Y':      os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_UVISTA_Y.header',  
                    'COSMOS_INT_UVISTA_J':  os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_INT_UVISTA_J.header',  
                    'COSMOS_INT_UVISTA_H':  os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_INT_UVISTA_H.header',  
                    'COSMOS_INT_UVISTA_K':  os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_INT_UVISTA_K.header',  
                    'COSMOS_INT_UVISTA_Y':  os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_INT_UVISTA_Y.header',  
                    'COSMOS_INT_IRAC_ch1':  os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_INT_IRAC_ch1.header',  
                   #'COSMOS_INT_IRAC_ch2':  os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_INT_IRAC_ch2.header',  
                   #'COSMOS_INT_IRAC_ch3':  os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_INT_IRAC_ch3.header',  
                   #'COSMOS_INT_IRAC_ch4':  os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_INT_IRAC_ch4.header',  
                    'COSMOS_ACS_i':         os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_ACS_i.header',  
                   #'COSMOS_ACS_F814W':     os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_ACS_F814W.header',  
                    'COSMOS_VLA_3GHz':      os.path.dirname(os.path.abspath(__file__))+os.sep+'a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL_image_header_caches'+os.sep+'COSMOS_VLA_3GHz.header', 
    }
    return Image_header_cache_dict



# query_cosmos_cutouts_via_IRSA_HTTP_URL
def query_cosmos_cutouts_via_IRSA_HTTP_URL(Source_Coordinate_Box, Cutout_Field, Cutout_Band, Output_Folder, Http_User_Name = '', Http_User_Pass = '', Overwrite_Level = 0): 
    # 
    # Check Output_Folder
    if Output_Folder != '':
        if not Output_Folder.endswith(os.sep):
            Output_Folder += os.sep
        if not os.path.isdir(Output_Folder):
            os.makedirs(Output_Folder)
    
    # 
    # Prepare Output File List
    Output_File_List = []
    
    # 
    # Check input Band and convert to IRSA-acceptable Image Names, and set Output_Name
    Image_url = ''
    Image_header_cache = ''
    Image_url_dict = get_IRSA_image_url_dict()
    Image_header_cache_dict = get_IRSA_image_header_cache_dict()
    # 
    Image_url = ''
    Image_header_cache = ''
    for t in [  Cutout_Field+'_'+Cutout_Band, 
                Cutout_Field+'_'+Cutout_Band.upper(), 
                Cutout_Field.upper()+'_'+Cutout_Band, 
                Cutout_Field.upper()+'_'+Cutout_Band.upper() ]:
        if t in Image_url_dict:
            Image_url = Image_url_dict[t]
            Output_Name = t
            if t in Image_header_cache_dict:
                Image_header_cache = Image_header_cache_dict[t]
            break
    if Image_url == '':
        print('Error! The input Field and Band "%s" is not in our Image Url list!'%(Cutout_Field+'_'+Cutout_Band))
        sys.exit()
    
    
    # Check input id
    if Source_Coordinate_Box['ID'] != '':
        Cutout_Field_and_ID = Cutout_Field+'_ID_%s'%(Source_Coordinate_Box['ID'])
    else:
        Cutout_Field_and_ID = Cutout_Field
    
    
    
    
    # Print Settings
    print('Image_url = "%s"'%(Image_url))
    print('Source RA = %s [deg]'%(Source_Coordinate_Box['RA']))
    print('Source Dec = %s [deg]'%(Source_Coordinate_Box['Dec']))
    print('Source FoV = %s [arcsec]'%(Source_Coordinate_Box['FoV']))
    print('Source PX = %s [pix]'%(Source_Coordinate_Box['PX']))
    print('Source PY = %s [pix]'%(Source_Coordinate_Box['PY']))
    print('Source DX = %s [pix]'%(Source_Coordinate_Box['DX']))
    print('Source DY = %s [pix]'%(Source_Coordinate_Box['DY']))
    print('Cutout_Field = %s'%(Cutout_Field))
    print('Cutout_Band = %s'%(Cutout_Band))
    print('Cutout_Field_and_ID = %s'%(Cutout_Field_and_ID))
    print('Output_Folder = "%s"'%(Output_Folder))
    print('Output_Name = "%s"'%(Output_Name))
    
    
    # write ds9 reg
    with open(Output_Folder+Cutout_Field_and_ID+'_'+Cutout_Band+'.ds9.reg','w') as fp:
        fp.write('# Region file format: DS9\n')
        fp.write('fk5\n')
        fp.write('box(%s,%s,%s",%s")\n'%(Source_Coordinate_Box['RA'], Source_Coordinate_Box['Dec'], Source_Coordinate_Box['FoV'], Source_Coordinate_Box['FoV']))
    
    
    # output subfolder for each band
    Output_SubFolder = Cutout_Field_and_ID+'_'+Cutout_Band + os.sep
    if not os.path.isdir(Output_Folder+Output_SubFolder):
        os.makedirs(Output_Folder+Output_SubFolder)
    
    
    # check header.txt to speed up
    if os.path.isfile(Image_header_cache+'.txt') and os.path.isfile(Image_header_cache+'.json'):
        Header_Cache_Txt = Image_header_cache+'.txt'
        Header_Cache_Json = Image_header_cache+'.json'
    else:
        Header_Cache_Txt = Output_Folder+Output_SubFolder+Output_Name+'.header.txt'
        Header_Cache_Json = Output_Folder+Output_SubFolder+Output_Name+'.header.json'
        # we need fits headers to determine how many bytes to shift 
        # if we have not downloaded the fits header files before, then download the into target directory.
    
    
    # Http_Request_Url
    Http_Request_Url = Image_url
    print('Header_Cache_Txt = %s'%(Header_Cache_Txt))
    print('Header_Cache_Json = %s'%(Header_Cache_Json))
    print('Http_Request_Url = %s'%(Http_Request_Url))
    
    
    
    # Proceed
    with requests.Session() as Http_Request_Session:
        
        Http_Request_Auth = None
        
        Output_Name = re.sub(r'\.fits$', '', os.path.basename(Http_Request_Url))
        
        if not os.path.isfile(Header_Cache_Txt) or Overwrite_Level >= 2:
            # 
            # Log in if Cutout_Field == 'COSMOS_INT'
            if Http_Request_Auth is None:
                if Cutout_Field == 'COSMOS_INT':
                    print('Cutout_Field is COSMOS_INT! We are logging in...')
                    if Http_User_Name == '':
                        if os.getenv('COSMOS_INT_USERNAME') is not None:
                            Http_User_Name = os.getenv('COSMOS_INT_USERNAME')
                        else:
                            Http_User_Name = input("Please enter http user name: ")
                    if Http_User_Pass == '':
                        if os.getenv('COSMOS_INT_PASSWORD') is not None:
                            Http_User_Pass = os.getenv('COSMOS_INT_PASSWORD')
                        else:
                            Http_User_Pass = getpass("Please enter http user password: ")
                    Http_Request_Auth = requests.auth.HTTPBasicAuth(Http_User_Name, Http_User_Pass) # see -- http://docs.python-requests.org/en/master/user/authentication/
                    print('Http_Request_Auth = %s'%(Http_Request_Auth))
            # 
            Http_Request_Head = Http_Request_Session.head(Http_Request_Url, allow_redirects=True, auth=Http_Request_Auth) # see -- http://docs.python-requests.org/en/master/user/authentication/
            print(Http_Request_Head.headers)
            print(Http_Request_Head.cookies)
            # 
            if not 'Accept-Ranges' in Http_Request_Head.headers:
                print('Error! The server does not support Http Range header! Exit!')
                sys.exit()
            # 
            Http_Request_Offset = 0
            Http_Request_Length = 2880 # 80*36, 36 lines of the FITS header
            #Http_Request_Content = '' # to store FITS header
            Flag_END = False # whether we have read the END mark
            FITS_Header_Length1 = 0
            FITS_Header_Length2 = 0
            # 
            with open(Header_Cache_Txt, 'w') as fp:
                while Http_Request_Offset < int(Http_Request_Head.headers['Content-Length']):
                    Http_Request_Range = {'Range': 'bytes=%d-%d'%(Http_Request_Offset, Http_Request_Offset+Http_Request_Length-1)}
                    print('')
                    print(Http_Request_Range)
                    Http_Request_Get = Http_Request_Session.get(Http_Request_Url, headers=Http_Request_Range, auth=Http_Request_Auth)
                    #print(Http_Request_Get)
                    if Http_Request_Get.status_code == 206:
                        Http_Request_Content = Http_Request_Get.content # Http_Request_Get.text
                        for i in range(0,len(Http_Request_Content),80):
                            try:
                                print('Http_Request_Content[%d:%d] = %s | %s (non-ASCII = %s)'%(Http_Request_Offset+i, Http_Request_Offset+i+80, bytes_to_hex_str(Http_Request_Content[i:i+4]), Http_Request_Content[i:i+80].decode("utf-8").rstrip(), check_non_ascii(Http_Request_Content[i:i+80]) ) )
                            except:
                                print('Http_Request_Content[%d:%d] = %s | %s (non-ASCII = %s)'%(Http_Request_Offset+i, Http_Request_Offset+i+80, bytes_to_hex_str(Http_Request_Content[i:i+4]), Http_Request_Content[i:i+80], check_non_ascii(Http_Request_Content[i:i+80]) ) )
                            # 
                            if check_non_ascii(Http_Request_Content[i:i+80]):
                                FITS_Header_Length2 = Http_Request_Offset + i
                                break
                            elif Http_Request_Content[i:i+80].decode("utf-8").rstrip() == 'END':
                                Flag_END = True
                                FITS_Header_Length1 = Http_Request_Offset + i + 80
                            fp.write(Http_Request_Content[i:i+80].decode("utf-8")+'\n')
                    elif Http_Request_Get.status_code == 200:
                        print('Error! Remote server does not support Http Range request!')
                        with open(Output_Folder+Output_SubFolder+Output_Name+'.header.http.request.json', 'w') as jfp:
                            json.dump({'Http_Request_Offset': Http_Request_Offset, 'Http_Request_Length': Http_Request_Length}, jfp)
                        sys.exit()
                    else:
                        print('Error! Connection broken!')
                        with open(Output_Folder+Output_SubFolder+Output_Name+'.header.http.request.json', 'w') as jfp:
                            json.dump({'Http_Request_Offset': Http_Request_Offset, 'Http_Request_Length': Http_Request_Length}, jfp)
                        sys.exit()
                    # 
                    if Flag_END and FITS_Header_Length2 > 0:
                        if os.path.isfile(Output_Folder+Output_SubFolder+Output_Name+'.header.http.request.json'):
                            os.remove(Output_Folder+Output_SubFolder+Output_Name+'.header.http.request.json')
                        break
                    # 
                    Http_Request_Offset = Http_Request_Offset + Http_Request_Length
                    #Http_Request_Content = ''
            # 
            with open(Header_Cache_Json, 'w') as jfp:
                json.dump({'FITS_Header_Length': FITS_Header_Length2, 'FITS_Total_Length': int(Http_Request_Head.headers['Content-Length'])}, jfp)
            #print('FITS_Header_Length = %d'%(FITS_Header_Length2))
        
        
        
        if not os.path.isfile(Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits') or Overwrite_Level >= 1:
            # 
            # Log in if Cutout_Field == 'COSMOS_INT'
            if Http_Request_Auth is None:
                if Cutout_Field == 'COSMOS_INT':
                    print('Cutout_Field is COSMOS_INT! We are logging in...')
                    if Http_User_Name == '':
                        if os.getenv('COSMOS_INT_USERNAME') is not None:
                            Http_User_Name = os.getenv('COSMOS_INT_USERNAME')
                        else:
                            Http_User_Name = input("Please enter http user name: ")
                    if Http_User_Pass == '':
                        if os.getenv('COSMOS_INT_PASSWORD') is not None:
                            Http_User_Pass = os.getenv('COSMOS_INT_PASSWORD')
                        else:
                            Http_User_Pass = getpass("Please enter http user password: ")
                    Http_Request_Auth = requests.auth.HTTPBasicAuth(Http_User_Name, Http_User_Pass) # see -- http://docs.python-requests.org/en/master/user/authentication/
                    print('Http_Request_Auth = %s'%(Http_Request_Auth))
            # 
            print('')
            print('')
            print('Prepare to download '+Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits')
            with open(Header_Cache_Json, 'r') as jfp:
                # 
                # Read FITS header length in (bytes)
                jdict = json.load(jfp)
                FITS_Header_Length = jdict['FITS_Header_Length']
                print('FITS_Header_Length = %s'%(FITS_Header_Length))
                
                # 
                # Generate FITS header object
                FITS_Header_Object = Header.fromfile(Header_Cache_Txt, sep='\n', endcard=False, padding=False) # , output_verify='ignore'
                FITS_Data_Unit_Byte = 4 # float/float16 type 
                if str(FITS_Header_Object['BITPIX']).strip() == '-64':
                    FITS_Data_Unit_Byte = 8 # double/float32 type 
                print('FITS_Data_Unit_Byte = %s'%(FITS_Data_Unit_Byte))
                
                # 
                # Fix NAXIS
                #if FITS_Header_Object['NAXIS']
                
                # 
                # Generate FITS header WCS
                FITS_Header_WCS = WCS(FITS_Header_Object, naxis=2)
                print(FITS_Header_WCS.printwcs())
                print('')
                
                # 
                # convert sky2xy or xy2sky
                if (numpy.isnan(Source_Coordinate_Box['PX']) or numpy.isnan(Source_Coordinate_Box['PY'])) \
                    and ~(numpy.isnan(Source_Coordinate_Box['RA']) or numpy.isnan(Source_Coordinate_Box['Dec'])):
                    Source_Coordinate_Box['PX'], Source_Coordinate_Box['PY'] = FITS_Header_WCS.wcs_world2pix(Source_Coordinate_Box['RA'], Source_Coordinate_Box['Dec'], 1)
                elif ~(numpy.isnan(Source_Coordinate_Box['PX']) or numpy.isnan(Source_Coordinate_Box['PY'])) \
                    and (numpy.isnan(Source_Coordinate_Box['RA']) or numpy.isnan(Source_Coordinate_Box['Dec'])):
                    Source_Coordinate_Box['RA'], Source_Coordinate_Box['Dec'] = FITS_Header_WCS.wcs_pix2world(Source_Coordinate_Box['PX'], Source_Coordinate_Box['PY'], 1)
                else:
                    print('Error! Either both RA Dec are invalid or both PX PY are invalid!')
                    print('Source_Coordinate_Box', Source_Coordinate_Box)
                    sys.exit()
                
                # 
                # print x y
                print('Source PX = %s [pix]'%(Source_Coordinate_Box['PX']))
                print('Source PY = %s [pix]'%(Source_Coordinate_Box['PY']))
                
                # 
                # check x y
                if Source_Coordinate_Box['PX']<1:
                    print('Error! Source x coordinate < 1!')
                    sys.exit()
                elif Source_Coordinate_Box['PX']>int(FITS_Header_Object['NAXIS1']):
                    print('Error! Source x coordinate > NAXIS1 (%d)!'%(int(FITS_Header_Object['NAXIS1'])))
                    sys.exit()
                elif Source_Coordinate_Box['PY']<1:
                    print('Error! Source y coordinate < 1!')
                    sys.exit()
                elif Source_Coordinate_Box['PY']>int(FITS_Header_Object['NAXIS2']):
                    print('Error! Source y coordinate > NAXIS2 (%d)!'%(int(FITS_Header_Object['NAXIS2'])))
                    sys.exit()
                
                # 
                # convert pixscale
                FITS_Pixel_Scale = astropy.wcs.utils.proj_plane_pixel_scales(FITS_Header_WCS)
                FITS_Pixel_Scale = numpy.array(FITS_Pixel_Scale) * 3600.0
                print('FITS_Pixel_Scale = %s arcsec'%(FITS_Pixel_Scale))
                
                # 
                # convert FoV to DX DY
                if (numpy.isnan(Source_Coordinate_Box['DX']) or numpy.isnan(Source_Coordinate_Box['DY'])) \
                    and ~(numpy.isnan(Source_Coordinate_Box['FoV'])):
                    Source_Coordinate_Box['DX'] = numpy.abs(Source_Coordinate_Box['FoV'] / FITS_Pixel_Scale[0])
                    Source_Coordinate_Box['DY'] = numpy.abs(Source_Coordinate_Box['FoV'] / FITS_Pixel_Scale[1])
                
                # 
                # print dx dy
                print('Source DX = %s [pix]'%(Source_Coordinate_Box['DX']))
                print('Source DY = %s [pix]'%(Source_Coordinate_Box['DY']))
                
                # 
                # check x y
                if Source_Coordinate_Box['PX']-Source_Coordinate_Box['DX']<1:
                    print('Error! Cutout lower x coordinate < 1!')
                    sys.exit()
                elif Source_Coordinate_Box['PX']+Source_Coordinate_Box['DX']>int(FITS_Header_Object['NAXIS1']):
                    print('Error! Cutout upper x coordinate > NAXIS1 (%d)!'%(int(FITS_Header_Object['NAXIS1'])))
                    sys.exit()
                elif Source_Coordinate_Box['PY']-Source_Coordinate_Box['DY']<1:
                    print('Error! Cutout lower y coordinate < 1!')
                    sys.exit()
                elif Source_Coordinate_Box['PY']+Source_Coordinate_Box['DY']>int(FITS_Header_Object['NAXIS2']):
                    print('Error! Cutout upper y coordinate > NAXIS2 (%d)!'%(int(FITS_Header_Object['NAXIS2'])))
                    sys.exit()
                
                # 
                # define cutout box
                Source_Coordinate_Box['Cutout_LowerX'] = int(Source_Coordinate_Box['PX'] - Source_Coordinate_Box['DX']/2.0)
                Source_Coordinate_Box['Cutout_UpperX'] = int(Source_Coordinate_Box['PX'] + Source_Coordinate_Box['DX']/2.0)
                Source_Coordinate_Box['Cutout_LowerY'] = int(Source_Coordinate_Box['PY'] - Source_Coordinate_Box['DY']/2.0)
                Source_Coordinate_Box['Cutout_UpperY'] = int(Source_Coordinate_Box['PY'] + Source_Coordinate_Box['DY']/2.0)
                sys.stdout.write('FITS_Header_WCS.calc_footprint() = ') # print()
                pprint(FITS_Header_WCS.calc_footprint(), indent=4)
                FITS_Header_WCS.footprint_to_file(Output_Folder+Output_SubFolder+Output_Name+'.cutout.footprint.ds9.reg', color='green', width=2)
                #with open(Output_Folder+Output_SubFolder+Output_Name+'.cutout.footprint.json', 'w') as jfp:
                #    json.dump(FITS_Header_WCS.calc_footprint().tolist(), jfp)
                #print(FITS_Header_Object['NAXIS1'])
                #cutout = Cutout2D(pf[0].data, position, size, wcs=wcs)
                sys.stdout.write('Source_Coordinate_Box = ') # print()
                pprint(Source_Coordinate_Box, indent=4)
                
                # 
                # Prepare new fits header and write to fits file
                FITS_Header_Object2 = copy(FITS_Header_Object)
                FITS_Header_Object2['NAXIS1'] = Source_Coordinate_Box['Cutout_UpperX'] - Source_Coordinate_Box['Cutout_LowerX'] + 1
                FITS_Header_Object2['NAXIS2'] = Source_Coordinate_Box['Cutout_UpperY'] - Source_Coordinate_Box['Cutout_LowerY'] + 1
                FITS_Header_Object2['CRPIX1'] = FITS_Header_Object2['CRPIX1'] - (Source_Coordinate_Box['Cutout_LowerX']-1)
                FITS_Header_Object2['CRPIX2'] = FITS_Header_Object2['CRPIX2'] - (Source_Coordinate_Box['Cutout_LowerY']-1)
                FITS_Header_Object2.tofile(Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits', sep='', endcard=True, padding=True, overwrite=True)
                Cutout_Data_Length = FITS_Header_Object2['NAXIS1'] * FITS_Header_Object2['NAXIS2'] * FITS_Data_Unit_Byte
                
                # 
                # Http request range
                Download_loop = Source_Coordinate_Box['Cutout_LowerY']
                Download_step = Source_Coordinate_Box['Cutout_UpperY'] - Source_Coordinate_Box['Cutout_LowerY']
                if Download_step > 50:
                    Download_step = 50 # must devide into multiple loops, because each request should not be too long
                while Download_loop <= Source_Coordinate_Box['Cutout_UpperY']:
                    
                    Http_Request_Range = {'Range': 'bytes=', 'Content-Type': 'multipart/byteranges'}
                    
                    if Download_loop+Download_step > Source_Coordinate_Box['Cutout_UpperY']:
                        Download_step = Source_Coordinate_Box['Cutout_UpperY'] - Download_loop
                    
                    for y in numpy.arange(Download_loop, Download_loop+Download_step+1, 1):
                        Http_Request_Offset_1 = FITS_Header_Length + FITS_Data_Unit_Byte * ((y-1) * int(FITS_Header_Object['NAXIS1']) + (Source_Coordinate_Box['Cutout_LowerX']-1))
                        Http_Request_Offset_2 = FITS_Header_Length + FITS_Data_Unit_Byte * ((y-1) * int(FITS_Header_Object['NAXIS1']) + (Source_Coordinate_Box['Cutout_UpperX']-1)) + FITS_Data_Unit_Byte-1
                        #if Http_Request_Offset_2>int(Http_Request_Head.headers['Content-Length']):
                        #    print('Error! Requested range too large!')
                        print('Http_Request_Offset = %d-%d (X:%d-%d, Y:%d)'%(Http_Request_Offset_1, Http_Request_Offset_2, Source_Coordinate_Box['Cutout_LowerX'], Source_Coordinate_Box['Cutout_UpperX'], y))
                        if Http_Request_Range['Range'] == 'bytes=':
                            Http_Request_Range['Range'] = Http_Request_Range['Range'] + '%d-%d'%(Http_Request_Offset_1, Http_Request_Offset_2)
                        else:
                            Http_Request_Range['Range'] = Http_Request_Range['Range'] + ',%d-%d'%(Http_Request_Offset_1, Http_Request_Offset_2)
                    
                    Download_loop = Download_loop+Download_step+1
                    
                    #Http_Request_Range['Transfer-Length'] = '%d'%(Cutout_Data_Length)
                    
                    sys.stdout.write('Http_Request_Range = ') # print()
                    pprint(Http_Request_Range, indent=4)
                    
                    # 
                    # Http request get -- partially get byte ranges -- then append to fits file
                    with open(Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits', 'ab') as fp:
                        Http_Request_Get = Http_Request_Session.get(Http_Request_Url, headers=Http_Request_Range, auth=Http_Request_Auth, stream=True)
                        print(Http_Request_Get)
                        if Http_Request_Get.status_code == 206:
                            #Http_Request_Content = Http_Request_Get.content
                            # To read multi byte range request content, we need the help of requests_toolbelt.multipart.decoder.MultipartDecoder
                            Http_Request_Content = MultipartDecoder.from_response(Http_Request_Get) # see -- https://github.com/requests/toolbelt/blob/master/requests_toolbelt/multipart/decoder.py
                            for part in Http_Request_Content.parts:
                                #pprint(part.text())
                                fp.write(part.content)
                            #if len(Http_Request_Content) > Cutout_Data_Length:
                            #    Http_Request_Content_Cutoff = 0
                            #    j = 0
                            #    #while j < len(Http_Request_Content):
                            #    #    if Http_Request_Content[j:j+4] == bytes.fromhex('0d0a2d2d'):
                            #    #        Http_Request_Content_Cutoff = 1
                            #    #    k = j+101
                            #    #    while k < len(Http_Request_Content):
                            #    #        if Http_Request_Content[k:k+4] == bytes.fromhex('0d0a0d0a'):
                            #    #        
                            #    #    j = j + 1
                            #fp.write(Http_Request_Content)
                            #for chunk in Http_Request_Get.iter_content(chunk_size=128):
                            #    fp.write(chunk)
                            #print(binascii.hexlify(copy(Http_Request_Content)))
                        elif Http_Request_Get.status_code == 200:
                            print('Error! Remote server does not support Http Range request!')
                            with open(Output_Folder+Output_SubFolder+Output_Name+'.cutout.http.request.json', 'w') as jfp:
                                json.dump(Http_Request_Range, jfp)
                            os.system('rm '+Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits')
                            sys.exit()
                        elif Http_Request_Get.status_code == 416:
                            print('Error! Requested range out of limit!')
                            with open(Output_Folder+Output_SubFolder+Output_Name+'.cutout.http.request.json', 'w') as jfp:
                                json.dump(Http_Request_Range, jfp)
                            os.system('rm '+Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits')
                            sys.exit()
                        else:
                            print('Error! Connection broken!')
                            with open(Output_Folder+Output_SubFolder+Output_Name+'.cutout.http.request.json', 'w') as jfp:
                                json.dump(Http_Request_Range, jfp)
                            os.system('rm '+Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits')
                            sys.exit()
            print('')
            print('Output to "'+Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits"!')
            Output_File_List.append(Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits')
        
        else:
            
            print('')
            print('Found existing "'+Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits"! We will not re-download it unless provided -overwrite.')
            print('')
            Output_File_List.append(Output_Folder+Output_SubFolder+Output_Name+'.cutout.fits')
        
    # 
    return Output_File_List








# 
# main
# 
if __name__ == '__main__':
    
    Source_Coordinate_Box = generate_query_dict()
    
    # Print usage
    if len(sys.argv) == 1:
        print('Usage: ')
        print('  a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL.py  -ra XXX -dec XXX -fov XXX -id XXX -out XXX -field COSMOS -band ACS_i')
        print('  a3cosmos_cutouts_query_cosmos_cutouts_via_IRSA_HTTP_URL.py  -ra XXX -dec XXX -fov XXX -id XXX -out XXX -field COSMOS_INT -band IRAC_ch1 -http-user-name XXX -http-user-pass XXX')
        print('')
        sys.exit()
    
    # Preset
    Output_Folder = ''
    Cutout_Field = 'COSMOS_INT'
    Cutout_Band = ''
    Http_User_Name = ''
    Http_User_Pass = ''
    Overwrite_Level = 0
    
    # Read User Input
    i = 1
    while i < len(sys.argv):
        tmp_arg = sys.argv[i].lower().replace('--','-')
        if tmp_arg == '-id':
            if i+1 < len(sys.argv):
                Source_Coordinate_Box['ID'] = sys.argv[i+1]
                i = i + 1
        elif tmp_arg == '-ra':
            if i+1 < len(sys.argv):
                Source_Coordinate_Box['RA'] = float(sys.argv[i+1])
                i = i + 1
        elif tmp_arg == '-dec':
            if i+1 < len(sys.argv):
                Source_Coordinate_Box['Dec'] = float(sys.argv[i+1])
                i = i + 1
        elif tmp_arg == '-fov':
            if i+1 < len(sys.argv):
                Source_Coordinate_Box['FoV'] = float(sys.argv[i+1])
                i = i + 1
        elif tmp_arg == '-out':
            if i+1 < len(sys.argv):
                Output_Folder = sys.argv[i+1]
                i = i + 1
        elif tmp_arg == '-field':
            if i+1 < len(sys.argv):
                Cutout_Field = sys.argv[i+1].replace('-','_')
                i = i + 1
        elif tmp_arg == '-band':
            if i+1 < len(sys.argv):
                Cutout_Band = sys.argv[i+1].replace('-','_').replace(' ','_')
                i = i + 1
        elif tmp_arg == '-http-username' or tmp_arg == '-http-user-name':
            if i+1 < len(sys.argv):
                Http_User_Name = sys.argv[i+1]
                i = i + 1
        elif tmp_arg == '-http-userpass' or tmp_arg == '-http-user-pass':
            if i+1 < len(sys.argv):
                Http_User_Pass = sys.argv[i+1]
                i = i + 1
        elif tmp_arg == '-overwrite':
            Overwrite_Level = Overwrite_Level + 1
        else:
            if numpy.isnan(Source_Coordinate_Box['RA']):
                Source_Coordinate_Box['RA'] = float(sys.argv[i])
            elif numpy.isnan(Source_Coordinate_Box['Dec']):
                Source_Coordinate_Box['Dec'] = float(sys.argv[i])
            elif numpy.isnan(Source_Coordinate_Box['FoV']):
                Source_Coordinate_Box['FoV'] = float(sys.argv[i])
        i = i + 1
    
    # Check User Input
    if (numpy.isnan(Source_Coordinate_Box['RA']) or numpy.isnan(Source_Coordinate_Box['Dec']) or numpy.isnan(Source_Coordinate_Box['FoV'])) \
        and (numpy.isnan(Source_Coordinate_Box['PX']) or numpy.isnan(Source_Coordinate_Box['PY']) or numpy.isnan(Source_Coordinate_Box['DX']) or numpy.isnan(Source_Coordinate_Box['DY'])):
        print('Please input RA Dec and FoV, or PX PY and DX DY!')
        sys.exit()
    if Cutout_Band == '':
        print('Please input Band!')
        sys.exit()
    
    # query_cosmos_cutouts_via_IRSA_HTTP_URL
    query_cosmos_cutouts_via_IRSA_HTTP_URL(Source_Coordinate_Box, Cutout_Field, Cutout_Band, Output_Folder = Output_Folder, Http_User_Name = Http_User_Name, Http_User_Pass = Http_User_Pass, Overwrite_Level = Overwrite_Level)





