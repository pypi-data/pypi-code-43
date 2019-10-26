from datetime import datetime


from decotra.s3 import track


def __o_add(num: int):
    """9->09 formatter"""
    return str(num) if num > 9 else f"0{num}"


__version__ = "0.0.3-dev"

__d = datetime.now()
saved_prefix = f"{__o_add(__d.year)}-{__o_add(__d.month)}-{__o_add(__d.day)}-{__o_add(__d.hour)}-{__o_add(__d.minute)}/"
