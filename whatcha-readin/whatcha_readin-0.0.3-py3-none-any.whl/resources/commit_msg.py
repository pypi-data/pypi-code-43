#!/usr/bin/env python3

import sys
from whatcha_readin.goodreads import get_currently_reading

currently_reading = get_currently_reading()

# append the books to the existing commit message
with open(sys.argv[1], "a") as f:
    if currently_reading:
        f.write("\nBooks-reading:")
    for book in currently_reading:
        f.write("\n{}".format(book))
