#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Usage: 
#    ./a3cosmos_cutouts_make_cutouts_for_input_images_by_RA_Dec.py -image image1.fits image2.fits -ra XXX -dec XXX -FoV XXX
#

import os, sys, re, json
import numpy
import numpy as np
import astropy
from astropy.wcs import WCS
from astropy.io import fits
from copy import copy
from pprint import pprint
from datetime import datetime



# Initialize
def generate_query_dict():
    Source_Coordinate_Box = {
                            'RA': numpy.nan, 
                            'Dec': numpy.nan, 
                            'FoV': numpy.nan, 
                            'PX': numpy.nan, 
                            'PY': numpy.nan, 
                            'DX': numpy.nan, 
                            'DY': numpy.nan, 
                            'Cutout_LowerX': numpy.nan, 
                            'Cutout_LowerY': numpy.nan, 
                            'Cutout_UpperX': numpy.nan, 
                            'Cutout_UpperY': numpy.nan, 
                            'Cutout_LowerX_Padding': numpy.nan, 
                            'Cutout_LowerY_Padding': numpy.nan, 
                            'Cutout_UpperX_Padding': numpy.nan, 
                            'Cutout_UpperY_Padding': numpy.nan, 
                            'Cutout_LowerX_Mapping': numpy.nan, 
                            'Cutout_LowerY_Mapping': numpy.nan, 
                            'Cutout_UpperX_Mapping': numpy.nan, 
                            'Cutout_UpperY_Mapping': numpy.nan, 
                        }
    return Source_Coordinate_Box



# trim_fits_header_dimension
def trim_fits_header_dimension(Image_head_sci):
    print('Image_head_sci[\'NAXIS\'] = %d'%(Image_head_sci['NAXIS']))
    if Image_head_sci['NAXIS'] > 2:
        for ck in range(3,Image_head_sci['NAXIS']+1):
            for cs in ['NAXIS', 'CRVAL', 'CRPIX', 'CDELT', 'CTYPE', 'CUNIT']:
                if '%s%d'%(cs,ck) in Image_head_sci: 
                    del Image_head_sci['%s%d'%(cs,ck)]
                    print('del Image_head_sci[\'%s\']'%('%s%d'%(cs,ck)))
            for cj in range(1,Image_head_sci['NAXIS']+1):
                if 'PC%02d_%02d'%(ck,cj) in Image_head_sci: 
                    del Image_head_sci['PC%02d_%02d'%(ck,cj)]
                    print('del Image_head_sci[\'%s\']'%('PC%02d_%02d'%(ck,cj)))
                if 'PC%02d_%02d'%(cj,ck) in Image_head_sci: 
                    del Image_head_sci['PC%02d_%02d'%(cj,ck)]
                    print('del Image_head_sci[\'%s\']'%('PC%02d_%02d'%(cj,ck)))
        Image_head_sci['NAXIS'] = 2
    print('Image_head_sci[\'NAXIS\'] = %d'%(Image_head_sci['NAXIS']))
    #print(Image_head_sci)
    return Image_head_sci











# 
# main
# 
if __name__ == '__main__':
    
    # 
    # Check User Input and Print Usage If No User Input
    if len(sys.argv) <= 1:
        print('Usage:')
        print('  ./a3cosmos_cutouts_make_cutouts_for_input_images_by_RA_Dec.py -image image1.fits image2.fits -ra XXX -dec XXX -FoV XXX -out XXX.fits')
        print('')
        sys.exit()
    
    # 
    # Preset
    Output_Name = ''
    Input_Images = []
    Overwrite_Level = 0
    Source_Coordinate_Box = generate_query_dict()
    
    # 
    # Read User Input
    i = 1
    arg_mode = ''
    while i < len(sys.argv):
        tmp_arg = sys.argv[i].lower().replace('--','-')
        if tmp_arg == '-ra':
            arg_mode = ''
            if i+1 < len(sys.argv):
                Source_Coordinate_Box['RA'] = float(sys.argv[i+1])
                i = i + 1
        elif tmp_arg == '-dec':
            arg_mode = ''
            if i+1 < len(sys.argv):
                Source_Coordinate_Box['Dec'] = float(sys.argv[i+1])
                i = i + 1
        elif tmp_arg == '-fov':
            arg_mode = ''
            if i+1 < len(sys.argv):
                Source_Coordinate_Box['FoV'] = float(sys.argv[i+1])
                i = i + 1
        elif tmp_arg == '-out' or tmp_arg == '-output':
            arg_mode = ''
            if i+1 < len(sys.argv):
                Output_Name = sys.argv[i+1]
                if Output_Name.endswith('.cutout.fits'):
                    Output_Name = ''.join(Output_Name.rsplit('.cutout.fits',1)) # replace the last pattern
                elif Output_Name.endswith('.fits'):
                    Output_Name = ''.join(Output_Name.rsplit('.fits',1)) # replace the last pattern
                i = i + 1
        elif tmp_arg == '-image' or tmp_arg == '-image-file':
            arg_mode = 'image'
        elif tmp_arg == '-overwrite':
            arg_mode = ''
            Overwrite_Level = Overwrite_Level + 1
        else:
            if arg_mode == 'image':
                Input_Images.append(sys.argv[i])
            else:
                if numpy.isnan(Source_Coordinate_Box['RA']):
                    Source_Coordinate_Box['RA'] = float(sys.argv[i])
                elif numpy.isnan(Source_Coordinate_Box['Dec']):
                    Source_Coordinate_Box['Dec'] = float(sys.argv[i])
                elif numpy.isnan(Source_Coordinate_Box['FoV']):
                    Source_Coordinate_Box['FoV'] = float(sys.argv[i])
        i = i + 1
    
    # 
    # Check User Input
    if (numpy.isnan(Source_Coordinate_Box['RA']) or numpy.isnan(Source_Coordinate_Box['Dec']) or numpy.isnan(Source_Coordinate_Box['FoV'])) \
        and (numpy.isnan(Source_Coordinate_Box['PX']) or numpy.isnan(Source_Coordinate_Box['PY']) or numpy.isnan(Source_Coordinate_Box['DX']) or numpy.isnan(Source_Coordinate_Box['DY'])):
        print('Please input RA Dec and FoV, or PX PY and DX DY!')
        print(Source_Coordinate_Box)
        sys.exit()
    if len(Input_Images) == []:
        print('Please input images!')
        sys.exit()
    if Output_Name == '':
        print('Please set the output name!')
        sys.exit()
    if Output_Name.find(os.sep) >= 0:
        if not os.path.isdir(os.path.dirname(os.path.abspath(Output_Name))):
            os.makedirs(os.path.dirname(os.path.abspath(Output_Name)))
    if re.match(r'\.fits$', Output_Name, re.IGNORECASE):
        Output_Name = re.sub(r'\.fits$', r'', Output_Name, re.IGNORECASE)
    if numpy.isnan(Source_Coordinate_Box['FoV']):
        Source_Coordinate_Box['FoV'] = 15.0 # default Field of View 15.0 arcsec
    
    # 
    # Print Settings
    print('Source RA = %s [deg]'%(Source_Coordinate_Box['RA']))
    print('Source Dec = %s [deg]'%(Source_Coordinate_Box['Dec']))
    print('Source FoV = %s [arcsec]'%(Source_Coordinate_Box['FoV']))
    print('Source PX = %s [pix]'%(Source_Coordinate_Box['PX']))
    print('Source PY = %s [pix]'%(Source_Coordinate_Box['PY']))
    print('Source DX = %s [pix]'%(Source_Coordinate_Box['DX']))
    print('Source DY = %s [pix]'%(Source_Coordinate_Box['DY']))
    print('Output_Name = %s'%(Output_Name))
    print('Input_Images = %s'%(Input_Images))
    
    # 
    # Write DS9 REGION
    with open(Output_Name+'.ds9.reg','w') as fp:
        fp.write('# Region file format: DS9\n')
        fp.write('fk5\n')
        fp.write('box(%s,%s,%s",%s")\n'%(Source_Coordinate_Box['RA'], Source_Coordinate_Box['Dec'], Source_Coordinate_Box['FoV'], Source_Coordinate_Box['FoV']))
    
    # 
    # Prepare Output Image List
    Cutout_fits_struct = fits.HDUList()
    Cutout_file_name = Output_Name+'.fits'
    
    # 
    # Loop each input image to make cutouts
    if not os.path.isfile(Output_Name+'.fits') or Overwrite_Level >= 1:
        # 
        for i in range(len(Input_Images)):
            print('Reading "%s" (%d/%d)'%(Input_Images[i], i+1, len(Input_Images)))
            Input_Image = Input_Images[i]
            Image_extension = 0
            Image_data_sci, Image_head_sci = fits.getdata(Input_Image, Image_extension, header=True)
            while Image_head_sci['NAXIS'] == 0:
                try:
                    Image_extension = Image_extension + 1
                    Image_data_sci, Image_head_sci = fits.getdata(Input_Image, Image_extension, header=True)
                except:
                    print('Error! Failed to read 2D image data from "%s"! Tried %d extensions!'%(Input_Image, Image_extension+1))
                    sys.exit()
            if len(Image_data_sci.shape) > 2:
                print('Image_data_sci.shape = %s'%(str(Image_data_sci.shape)))
                if(np.prod(Image_data_sci.shape) == np.prod(Image_data_sci.shape[-2:])):
                    Image_data_sci = np.squeeze(Image_data_sci)
                else:
                    while (len(Image_data_sci.shape) > 2):
                        print('Image_data_sci = Image_data_sci.take(0, axis=%d)'%(0))
                        Image_data_sci = Image_data_sci.take(0, axis=0)
                    print(Image_data_sci.shape)
            # 
            Image_head_sci = trim_fits_header_dimension(Image_head_sci)
            Image_wcs = WCS(Image_head_sci)
            Image_pixscale = astropy.wcs.utils.proj_plane_pixel_scales(Image_wcs) * 3600.0 # arcsec
            Object_posxy = Image_wcs.wcs_world2pix(Source_Coordinate_Box['RA'], Source_Coordinate_Box['Dec'], 1) # the third parameter "1" means posxy starting from 1.
            print('Object_radec', Source_Coordinate_Box['RA'], Source_Coordinate_Box['Dec'])
            print('Object_posxy', Object_posxy)
            Object_FoV = Source_Coordinate_Box['FoV'] # 15.0 arcsec
            Object_side = Object_FoV / np.abs(Image_pixscale) # pixels
            Object_rect00 = np.floor(Object_posxy - Object_side/2.0 - 1).astype(int)
            Object_rect11 = np.ceil(Object_posxy + Object_side/2.0 - 1).astype(int)
            print('Object_rect', Object_rect00, Object_rect11)
            # 
            # prepare cutout for output
            Cutout_head_sci = copy(Image_head_sci)
            Cutout_head_sci['NAXIS1'] = Object_rect11[0]-Object_rect00[0]+1
            Cutout_head_sci['NAXIS2'] = Object_rect11[1]-Object_rect00[1]+1
            Cutout_head_sci['CRPIX1'] = Cutout_head_sci['CRPIX1'] - Object_rect00[0]
            Cutout_head_sci['CRPIX2'] = Cutout_head_sci['CRPIX2'] - Object_rect00[1]
            print('Cutout_head_sci[\'NAXIS\'] = %d'%(Cutout_head_sci['NAXIS']))
            # 
            Cutout_rect00 = np.array([0,0])
            Cutout_rect11 = Cutout_rect00 + Object_rect11-Object_rect00+1 - 1
            if Object_rect11[0]>0 and Object_rect11[1]>0:
                if Object_rect00[0]<0:
                    Cutout_rect00[0] = Cutout_rect00[0] - (Object_rect00[0] - 0)
                    Object_rect00[0] = 0
                if Object_rect00[1]<0:
                    Cutout_rect00[1] = Cutout_rect00[1] - (Object_rect00[1] - 0)
                    Object_rect00[1] = 0
                if Object_rect11[0]>(Image_head_sci['NAXIS1']-1):
                    Cutout_rect11[0] = Cutout_rect11[0] - (Object_rect11[0] - (Image_head_sci['NAXIS1']-1))
                    Object_rect11[0] = (Image_head_sci['NAXIS1']-1)
                if Object_rect11[1]>(Image_head_sci['NAXIS2']-1):
                    Cutout_rect11[1] = Cutout_rect11[1] - (Object_rect11[1] - (Image_head_sci['NAXIS2']-1))
                    Object_rect11[1] = (Image_head_sci['NAXIS2']-1)
                print('Object_rect', Object_rect00, Object_rect11)
                print('Cutout_rect', Cutout_rect00, Cutout_rect11)
                Cutout_data_sci = np.zeros((Cutout_head_sci['NAXIS2'],Cutout_head_sci['NAXIS1']))
                print('Cutout_data_sci.shape', Cutout_data_sci.shape)
                Cutout_data_sci[Cutout_rect00[1]:Cutout_rect11[1]+1, Cutout_rect00[0]:Cutout_rect11[0]+1 ] = Image_data_sci[Object_rect00[1]:Object_rect11[1]+1, Object_rect00[0]:Object_rect11[0]+1 ] # NOTE THAT PYTHON DIMENSION ORDER: [iY,iX]
            else:
                print('Object_rect upper x or y is negative! Return zero padded image!')
                Cutout_data_sci = np.zeros((Cutout_head_sci['NAXIS2'],Cutout_head_sci['NAXIS1']))
                print('Cutout_data_sci.shape', Cutout_data_sci.shape)
            # 
            Cutout_head_sci.append(('COMMENT', ''), bottom=True )
            
            Cutout_head_sci.append(('CUTFROM', os.path.abspath(Input_Image)), bottom=True )
            Cutout_head_sci.insert(Cutout_head_sci.index('CUTFROM')+1, ('COMMENT', 'CUTFROM: The fits image file where the cutout is made from.') )
            Cutout_head_sci.insert(Cutout_head_sci.index('CUTFROM')+2, ('COMMENT', '') )
            
            Cutout_head_sci.append(('CUTRECT', '(%d, %d), (%d, %d)'%(Object_rect00[0], Object_rect00[1], Object_rect11[0], Object_rect11[1])), bottom=True )
            Cutout_head_sci.insert(Cutout_head_sci.index('CUTRECT')+1, ('COMMENT', 'CUTRECT: The lower left (x,y) and upper right (x,y) coordinate of this cutout in the CUTFROM fits image. Coordinates have an origin of (1,1).') )
            Cutout_head_sci.insert(Cutout_head_sci.index('CUTRECT')+2, ('COMMENT', '') )
            
            Cutout_head_sci.append(('CUTDATE', datetime.today().strftime('%Y-%m-%d %Hh%Mm%Ss %Z')), bottom=True )
            Cutout_head_sci.append(('CUTCODE', os.path.abspath(__file__)), bottom=True )
            
            Cutout_head_sci.append(('COMMENT', ''), bottom=True )
            
            Cutout_head_sci.append(('EXTNAME', 'Cutout_%d'%(i+1)), bottom=True )
            
            Cutout_fits_struct.append(fits.ImageHDU(Cutout_data_sci, Cutout_head_sci, name='Cutout_%d'%(i+1), do_not_scale_image_data=True))
        
        # 
        # Final output
        Cutout_fits_struct.writeto(Cutout_file_name, overwrite=True)
        print('Output to cutout fits file "%s"!'%(Cutout_file_name))
    
    else:
        
        print('Found existing cutout fits file "%s"! Will not overwrite unless given -overwrite option!'%(Output_Name+'.fits'))










