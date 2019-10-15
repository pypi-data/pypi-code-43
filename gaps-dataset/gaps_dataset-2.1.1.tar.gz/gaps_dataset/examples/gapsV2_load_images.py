"""
Created on 2019/09/27

@author: Ronny Stricker
Example for creating patches from the patch location files.
"""

import os
import numpy as np
import cv2
import zipfile
import matplotlib.pyplot as plt
from gaps_dataset import gaps

#########

destination_directory = '/your/download/destination/directory'
login = 'yourlogin'
ds = 'test'
patchsize = 64

#########

# download images and segmentation masks
gaps.download(login=login,
              output_dir=destination_directory,
              version=2,
              patchsize='images',
              debug_outputs=True)

# unzip images
basedir = os.path.join(destination_directory, 'v2', 'images')
img_dir = os.path.join(basedir, 'images')

zip_filename = os.path.join(basedir, 'images.zip')
zip_ref = zipfile.ZipFile(zip_filename, 'r')
zip_ref.extractall(img_dir)
zip_ref.close()

patch_file = os.path.join(basedir, 'patch_references_{}.npz'.format(ds))
ps = patchsize / 2

# use variable old_img_name to avoid loading the input images for every single patch
old_img_id = None
img = None
patches = np.load(patch_file)['data']
for patch_id in range(patches.shape[0]):
    img_id, row, col, class_id = patches[patch_id]
    # load input image if it is different from the image used for the last patch
    if img_id != old_img_id:
        center = cv2.imread(os.path.join(img_dir, str(img_id).zfill(5) + '.jpg'))
        # add border to the image in order to draw patches without the need to check for image boundaries
        img = np.zeros((center.shape[0] + patchsize, center.shape[1] + patchsize, center.shape[2]), dtype=center.dtype)
        img[ps:ps + center.shape[0], ps:ps + center.shape[1]] = center
    old_img_id = img_id

    # draw patch from input image
    img_patch = img[row:row + patchsize, col:col + patchsize]
    assert img_patch.shape == (patchsize, patchsize, 3)

    # display patch
    plt.figure(num=str(class_id), figsize=(2, 2))
    plt.imshow(img_patch)
    plt.show()
