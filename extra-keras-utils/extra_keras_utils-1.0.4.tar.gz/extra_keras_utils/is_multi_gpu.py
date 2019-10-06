from .get_gpus_number import get_gpus_number

def is_multi_gpu() -> bool:
    return get_gpus_number()>1