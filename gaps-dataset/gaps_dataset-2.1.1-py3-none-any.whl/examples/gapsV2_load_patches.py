"""
Created on 2019/09/11

@author: Ronny Stricker
Example for downloading patches of GAPs v2 dataset and usage.
"""

from gaps_dataset import gaps

# change these parameters:
destination_directory = '/your/download/destination/directory'
login = 'yourlogin'

# download patches of the dataset
gaps.download(login=login,
              output_dir=destination_directory,
              version=2,
              patchsize=160,                # possible values: [64, 96, 128, 160, 192, 224, 256]
              issue='NORMvsDISTRESS_50k',   # possible values: ['NORMvsDISTRESS', 'NORMvsDISTRESS_50k', 'ZEB_50k']
              subsets=None,                 # possible values: [None, 'train', 'valid', 'valid-test', 'test']
              debug_outputs=True)

# load training dataset info file
train_info = gaps.get_dataset_info(version=2,
                                   patchsize=160,
                                   issue='NORMvsDISTRESS_50k',
                                   subset='train',
                                   datadir=destination_directory)

print("Training dataset info: {}".format(train_info))

# load all chunks of training dataset
for chunk_id in range(train_info['n_chunks']):
    x, y = gaps.load_chunk(chunk_id=chunk_id,
                           version=2,
                           patchsize=160,
                           issue='NORMvsDISTRESS_50k',
                           subset='train',
                           datadir=destination_directory)

    # binary_label:
    #    0 = intact road,
    #    1 = distress
    # class_label:
    #    0 = intact road,
    #    1 = applied patch,
    #    2 = pothole,
    #    3 = inlaid patch,
    #    4 = open joint,
    #    5 = crack

# replace train with valid or test respectively to extract patches of the other subsets
