from __future__ import print_function
import sys
import itertools
import warnings
import numpy as np
import skimage.io
from .. import reg


input_file = sys.argv[1]
output_dir = sys.argv[2]

channel = 0
if len(sys.argv) >= 4:
    channel = int(argv[3])

reader = reg.BioformatsReader(input_file)
metadata = reader.metadata
shape = metadata.grid_dimensions

total = metadata.num_images
locations = itertools.product(reversed(range(shape[0])), range(shape[1]))
for i, (row, col) in enumerate(locations):
    sys.stdout.write("\rCopying %d/%d" % (i + 1, total))
    sys.stdout.flush()
    img = reader.read(c=channel, series=i)
    output_file = output_dir + '/img_r{r:03}_c{c:03}.tif'.format(r=row, c=col)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            'ignore', r'.* is a low contrast image', UserWarning,
            '^skimage\.io'
        )
        skimage.io.imsave(output_file, img)
print()
