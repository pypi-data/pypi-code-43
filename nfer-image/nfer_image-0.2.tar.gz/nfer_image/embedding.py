import tensorflow as tf
from tensorflow import keras
import tensorflow.keras.backend as K
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.inception_v3 import InceptionV3
from tensorflow.keras.models import Model
from tqdm import tqdm
import os
import pandas as pd
import numpy as np
import time
import skimage.io
import pickle

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)

# dtype = 'float16'
# K.set_floatx(dtype)
# K.set_epsilon(1e-4)


"""
TO-DO
1) Write own generator. Currently using ImageDataGenerator in Keras
"""

def cnn_bottleneck_extraction(exp_name, img_dir, target_size=(299, 299)):

	# Load imagenet pre-trained InceptionV3
	base_model = InceptionV3(weights='imagenet')
	model = Model(inputs=base_model.input, outputs=base_model.get_layer('avg_pool').output)
	img_list = os.listdir(img_dir)
	image_features_df = pd.DataFrame(index=img_list, columns=list(range(2048)), dtype='float16')

	for img in tqdm(img_list):
	    img = image.load_img(os.path.join(img_dir,img), target_size=(299, 299))
	    x = image.img_to_array(img, dtype='float16')/255
	    x = np.expand_dims(x, axis=0)
	    feature_vec = model.predict(x)
	    image_features_df.loc[img] = feature_vec[0]


	image_features_df.to_csv('{}.csv'.format(exp_name), index_label='File')

	return image_features_df
