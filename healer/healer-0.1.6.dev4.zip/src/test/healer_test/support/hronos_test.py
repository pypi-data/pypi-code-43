
import time
from healer.support.hronos import *


def test_date_time():
    print()

    instant_list = [
        DateTime(2018, 11, 12),
        DateTime.now(),
        DateTime.utcnow(),
        DateTime.utcfromtimestamp(time.time())
    ]

    for instant in instant_list:
        print(f"instant: {instant} type: {type(instant)}")

