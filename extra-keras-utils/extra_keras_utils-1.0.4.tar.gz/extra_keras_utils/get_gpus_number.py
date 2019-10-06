from tensorflow.python.client.device_lib import list_local_devices

def get_gpus_number() -> int:
    return len([
        x.name for x in list_local_devices() if x.device_type == 'GPU'
    ])
