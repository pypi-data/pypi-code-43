"""
Created on 2019/09/11

@author: Ronny Stricker
Example for downloading patches of GAPs v1 dataset and usage.
"""

from gaps_dataset import gaps

# change these parameters:
destination_directory = '/your/download/destination/directory'
login = 'yourlogin'

# download patches (91 Gb!!)
gaps.download(login=login,
              output_dir=destination_directory,
              version=1,
              patchsize=64,                 # possible values: [64]
              issue='NORMvsDISTRESS',       # possible values: ['NORMvsDISTRESS']
              subsets=None,                 # possible values: [None, 'train', 'valid', 'test']
              debug_outputs=True)

# load training dataset info file
train_info = gaps.get_dataset_info(version=1,
                                   patchsize=64,
                                   issue='NORMvsDISTRESS',
                                   subset='train',
                                   datadir=destination_directory)

print("Training dataset info: {}".format(train_info))

# load all chunks of training dataset
for chunk_id in range(train_info['n_chunks']):
    x, y = gaps.load_chunk(chunk_id=chunk_id,
                           version=1,
                           patchsize=64,
                           issue='NORMvsDISTRESS',
                           subset='train',
                           datadir=destination_directory)

    # binary_label:
    #    0 = intact road,
    #    1 = distress

# replace train with valid or test respectively to extract patches of the other subsets
