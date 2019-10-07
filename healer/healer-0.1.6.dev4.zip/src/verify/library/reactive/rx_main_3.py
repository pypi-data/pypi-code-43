"""
https://github.com/ReactiveX/RxPY/issues/100
"""

import concurrent.futures
import rx
from rx import operators as ops


def custom_print_buffer(items):
    if items:
        print(len(items))


def custom_print(item):
    print(item)


def return_item(item):
    return item


print("init")

origin = rx.from_(range(3000))
with concurrent.futures.ThreadPoolExecutor(5) as executor:
    origin.pipe(
        ops.flat_map(lambda item: executor.submit(return_item, item)),
        ops.buffer_with_count(100)
    ).subscribe(custom_print_buffer)

print("done")
