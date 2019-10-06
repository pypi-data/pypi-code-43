import numpy as np
import random
import tensorflow as tf
import os
from keras import backend as K

def set_seed(seed:int, kill_parallelism:bool=False):
    """Set the random state of the various random extractions.
        seed:int, the seed to set the random state to.
        kill_parallelism:bool, whetever to kill parallelism to get full reproducibility.
    """
    os.environ['PYTHONHASHSEED']=str(seed)
    np.random.seed(seed)
    random.seed(seed)
    if kill_parallelism:
        K.set_session(
            tf.Session(
                graph=tf.get_default_graph(),
                config=tf.ConfigProto(
                    intra_op_parallelism_threads=1,
                    inter_op_parallelism_threads=1
                )
            )
        )
