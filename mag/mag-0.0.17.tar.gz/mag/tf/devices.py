from tensorflow.python.client import device_lib
import os, tensorflow as tf

def available_devices():
    '''

    Returns:
        devices(dict): a list of devices by type (cpu / gpu)
    '''
    devices = device_lib.list_local_devices()
    cpus = [d for d in devices if d.device_type == 'CPU']
    gpus = [d for d in devices if d.device_type == 'GPU']
    return {'cpus': cpus, 'gpus': gpus}


def gpu_available_q():
    '''
    Returns:
        (bool): whether or not there is an availble gpu
    '''
    return len(available_devices()['gpus']) > 0


def set_env_devices(devices:list):
    '''
    Sets the environment variable CUDA_VISIBLE_DEVICES to devices

    Args:
        devices(list): a list of device names

    Returns:
        None

    '''
    os.environ["CUDA_VISIBLE_DEVICES"] = ','.join(devices)

def restrict_gpu_devices(
    device_names:list=None,
    num_devices:int=None,
    verbose=False
):
    '''
    Utilizes experimental tf functions to restrict GPU devices. Must be called
    prior to other tf functions.

    Notes:
        - Only either `device_names` or `num_devices` can be set. `num_devices`
            takes precedent over `device_names`

    Arguments:
        device_names (list): Name of devices to use. Defaults to None. If None,
            uses all available devices

        num_devices (int): Number of devices to use. Defaults to None. Takes
            _first_ `num_devices` GPUs.

        verbose (bool): whether or not to print out devices. Defaults to False.

    Returns:
        None
    '''
    env_gpus = tf.config.experimental.list_physical_devices('GPU')
    if verbose:
        print('GPUs found in environment:\t', env_gpus)

    if device_names is not None:
        gpus = [g for g in env_gpus if g.name in device_names]

    if num_devices is not None:
        gpus = env_gpus[:num_devices]

    if verbose:
        print('GPUs found matching device names:\t', gpus)
    if gpus:
        try:
            tf.config.experimental.set_visible_devices(gpus, 'GPU')
            logical_gpus = tf.config.experimental.list_logical_devices('GPU')
            if verbose:
                print('Environment has {} physical GPUs'.format(env_gpus))
                print('Restricted to {} logical GPUs'.format(logical_gpus))
        except RuntimeError as e:
            # Visible devices must be set before GPUs have been initialized
            print(e)
    else:
        if verbose:
            print('No GPUs found.')
