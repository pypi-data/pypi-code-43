#!/usr/bin/env python3

import sys
from whatcha_readin.goodreads import get_currently_reading

currently_reading = get_currently_reading()

# get the original commit message
with open(sys.argv[1]) as f:
    msg = f.read()

# append the currently reading books
with open(sys.argv[1], "w") as f:
    f.write(msg)
    if currently_reading:
        f.write("\nBooks-reading:")
    for book in currently_reading:
        f.write("\n{}".format(book))
