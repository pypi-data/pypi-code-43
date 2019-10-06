from keras import backend as K

def is_gpu_available()->bool:
    return bool(K.tensorflow_backend._get_available_gpus())