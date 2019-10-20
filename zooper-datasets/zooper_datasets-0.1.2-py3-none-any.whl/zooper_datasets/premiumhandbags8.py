"""PREMIUMHANDBAGS8 small images classification dataset.
"""
import os
import shutil
import tarfile
import time

from keras.utils.data_utils import get_file


def load_data(target_dir='premium_handbags'):
    """Loads PREMIUMHANDBAGS8 dataset.
    # Returns
        Tuple of Numpy arrays: `(x_train, y_train), (x_test, y_test)`.
    """
    dirname = '/tmp/premium-handbags-8'
    origin = 'https://premium-handbags.s3-us-west-2.amazonaws.com/premium-handbags-8.tar.gz'

    st = time.time()
    path = get_file(dirname, origin=origin, untar=True)

    def tar_member(members):
        for tarinfo in members:
            yield tarinfo

    tar = tarfile.open(path + '.tar.gz')
    tar.extractall(members=tar_member(tar))
    tar.close()

    if os.path.isdir(target_dir):
        print('Deleting {} ...'.format(target_dir))
        shutil.rmtree(target_dir)
    if target_dir != 'premium_handbags':
        shutil.move('premium_handbags', target_dir)
    et = time.time()
    print('`premium_handbags` dataset downloaded to {}. Elapsed time: {} secs'.format(target_dir, (et - st)))
