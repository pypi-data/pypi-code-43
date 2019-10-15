    
def list_local_devices():
    """
    List local devices (GPUs and CPUs) using tensorflow's tensorflow.python.client.device_lib
    
    Returns:
    --------
        local_devices: list of 'DeviceAttributes' object. The DeviceAttributes.device_type value for each DeviceAttributes element in the list can be used to determine whether the device is a GPU or CPU.
    """
    from tensorflow.python.client import device_lib
    local_devices = device_lib.list_local_devices()
    return local_devices

def device_counts():
    """
    Count the number of CPUs and GPUs on the local machine.
    
    Returns:
    --------
        device_counts: dictionary with "CPUs" and "GPUs" keys associated with the device count for each.
    """
    local_devices = list_local_devices()
    
    device_counts = {'CPUs':len([dev for dev in local_devices if 'CPU' in dev.device_type]),
                   'GPUs':len([dev for dev in local_devices if 'GPU' in dev.device_type])
                  }
    return device_counts
                   
        