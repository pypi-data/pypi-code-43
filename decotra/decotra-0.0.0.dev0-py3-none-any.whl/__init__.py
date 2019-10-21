from datetime import datetime


from decotra.s3 import track


def o_add(num: int):
    """9->09 formatter"""
    return str(num) if num > 9 else f"0{num}"


__version__ = "0.0.0-dev"

d = datetime.now()
saved_prefix = f"{o_add(d.year)}-{o_add(d.month)}-{o_add(d.day)}-{o_add(d.hour)}-{o_add(d.minute)}/"
