""" 
Utilities include:
- image loading & download utility from s3 bucket
- image download from specific s3 bucket
- image save (pyplot based)
- image tiling
- stain estimation
"""

import skimage.io
import matplotlib.pyplot as plt
import cv2 as cv
import os
import time
from skimage.color import rgb2hed
from sklearn.feature_extraction.image import extract_patches_2d
import numpy as np
import gc
import tempfile
import pandas as pd
import boto3
from tqdm import tqdm
import pathlib
import random

def get_tissue_mask(I, luminosity_threshold=0.8):
    """
    Get a binary mask where true denotes pixels with a luminosity less than the specified threshold.
    Typically we use to identify tissue in the image and exclude the bright white background.
    :param I: RGB uint 8 image.
    :param luminosity_threshold: Luminosity threshold.
    :return: Binary mask.
    """
    # assert is_uint8_image(I), "Image should be RGB uint8."
    I_LAB = cv.cvtColor(I, cv.COLOR_RGB2LAB)
    L = I_LAB[:, :, 0] / 255.0  # Convert to range [0,1].
    mask = L < luminosity_threshold

    return mask

def get_ihc_mask(img):

    ihc_img = rgb2hed(img)
    ihc_mask = np.where(ihc_img[:,:,2]>-0.35, 1, 0)

    return ihc_mask

def ihc_stained_fraction(img_path):
    img = skimage.io.imread(img_path)
    tissue_mask = get_tissue_mask(img)
    ihc_mask = get_ihc_mask(img)

    return ihc_mask.sum()/tissue_mask.sum()

def stain_normalization(image, a_min=0.9, a_max=1.1, b_min=-0.039, b_max=0.039):
    # simple H&E color augmentation based on https://arxiv.org/pdf/1707.06183.pdf
    rn = random.uniform(0, 1)
    if rn > 0.3:
        image * np.random.uniform(a_min, a_max, image.shape) + np.random.uniform(b_min, b_max, image.shape)

    return image

def patch_extraction(img_dir, output_dir, patch_size, stained=False):


	for root, dirs, files in os.walk(img_dir):
		for file in files:
			if not file.endswith('.jpg'):
				continue
			img_path = os.path.join(root, file)
			img = skimage.io.imread(img_path)

			patch_list = list(extract_patches_2d(img, patch_size, max_patches=0.00001, random_state=2019))
			if stained:
				patch_list_filtered = [patch for patch in patch_list if np.where(rgb2hed(patch)[:,:,2]>-0.8, 1, 0).mean()>0.1]
			else:
				patch_list_filtered = [patch for patch in patch_list if get_tissue_mask(patch).mean()>0.3]
			random.shuffle(patch_list_filtered)
			patch_list_filtered = patch_list_filtered[:50]

			i = 1
			for patch in patch_list_filtered:
				fig = plt.imshow(patch)
				plt.axis('off')
				fig.axes.get_xaxis().set_visible(False)
				fig.axes.get_yaxis().set_visible(False)
				plt.savefig("{}/{}".format(output_dir, file.split('.')[0] +'_'+str(i)+'.jpg'), bbox_inches='tight', pad_inches = 0)
				plt.clf()
				plt.close()
				gc.collect()
				i+=1

def load_aws_img(session, host, bucket, url):
	s3 = session.resource('s3', region_name=host)
	bucket = s3.Bucket(bucket)
	object = bucket.Object(url)
	img_file = tempfile.NamedTemporaryFile()
	with open(img_file.name, 'wb') as f:
		object.download_fileobj(f)
	return img_file

def img_save(img, save_path):
	pathlib.Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
	fig = plt.imshow(img)
	plt.axis('off')
	fig.axes.get_xaxis().set_visible(False)
	fig.axes.get_yaxis().set_visible(False)
	plt.savefig(save_path, bbox_inches='tight', pad_inches = 0)
	plt.clf()
	plt.close()
	gc.collect()

def tile_extraction(img_file, file, tile_size, num_tiles=200, stained=True, output_dir=None):

	img = skimage.io.imread(img_file)

	# tile_list = list(extract_patches_2d(img, tile_size, max_patches=0.00001, random_state=2019))
	tile_list = list(extract_patches_2d(img, tile_size, max_patches=0.00005, random_state=2019))

	if stained:
		tile_list_filtered = [tile for tile in tile_list if get_tissue_mask(tile).mean()>0.3]
		tile_list_filtered = [tile for tile in tile_list_filtered if np.where(rgb2hed(tile)[:,:,2]>-0.8, 1, 0).mean()>0.1]
	else:
		tile_list_filtered = [tile for tile in tile_list if get_tissue_mask(tile).mean()>0.3]
	random.shuffle(tile_list_filtered)
	tile_list_filtered = tile_list_filtered[:num_tiles]

	if output_dir:
		i = 1
		for tile in tile_list_filtered:
			tile_path = "{}/{}".format(output_dir, file.split('.')[0] +'-'+str(i)+'.jpg')
			if os.path.exists(tile_path):
				tile_path = "{}/{}".format(output_dir, file.split('.')[0] +'-'+str(i)+'a.jpg')
			img_save(tile, tile_path)
			i+=1
		print('{} tiles saved to {}'.format(len(tile_list_filtered), output_dir))

	return tile_list_filtered

def tiles_from_dataframe(file_df, url_column, tile_size, session, aws_host, aws_bucket_name, output_dir=None):


	file_df[url_column] = file_df.apply(lambda row: row[url_column].split('.com/')[1], axis=1)

	for index, row in tqdm(file_df.iterrows(), total=file_df.shape[0]):
		pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
		file = os.path.basename(row[url_column])
		img_file = load_aws_img(session, aws_host, aws_bucket_name, row[url_column])
		tile_list = tile_extraction(img_file, file, tile_size, output_dir=output_dir)

