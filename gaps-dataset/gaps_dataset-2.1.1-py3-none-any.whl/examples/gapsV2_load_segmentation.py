"""
Created on 2019/09/11

@author: Ronny Stricker
Example for downloading segmentation masks of GAPs v2 dataset.
"""

from gaps_dataset import gaps
import zipfile
import os

# change these parameters:
destination_directory = '/your/download/destination/directory'
login = 'yourlogin'

# download images and segmentation masks
gaps.download(login=login,
              output_dir=destination_directory,
              version=2,
              patchsize='segmentation',
              debug_outputs=True)

# unzip images and masks
basedir = os.path.join(destination_directory, 'v2', 'segmentation')

for f in ['images', 'train', 'valid', 'test', 'valid-test']:
    zip_filename = os.path.join(basedir, f + '.zip')
    zip_ref = zipfile.ZipFile(zip_filename, 'r')
    zip_ref.extractall(os.path.join(basedir, f))
    zip_ref.close()

# Mask images are stored as grey value images.
# Coding of the grey values:
#    0 = VOID
#    1 = intact road,
#    2 = applied patch,
#    3 = pothole,
#    4 = inlaid patch,
#    5 = open joint,
#    6 = crack
#    7 = street inventory
