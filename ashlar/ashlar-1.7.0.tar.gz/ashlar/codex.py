import re
import pathlib2 as pathlib
import numpy as np
import skimage.io
from . import reg



class CodexMetadata(reg.Metadata):

    def __init__(self, path, pattern, shape, overlap):
        self.path = pathlib.Path(path)
        self.pattern = pattern
        self.height, self.width = shape
        self.overlap = overlap
        self._enumerate_tiles()

    def _enumerate_tiles(self):
        regex = re.sub(r'{([^:}]+)(?:[^}]*)}', r'(?P<\1>.*?)',
                       self.pattern.replace('.', '\.'))
        tiles = set()
        channels = set()
        num_images = 0
        for p in self.path.iterdir():
            match = re.match(regex, p.name)
            if match:
                gd = match.groupdict()
                tiles.add(int(gd['tile']))
                channels.add(int(gd['channel']))
                num_images += 1
        if len(tiles) != self.height * self.width:
            raise Exception("Filenames are not consistent with grid shape")
        if len(tiles) * len(channels) != num_images:
            raise Exception("Missing some image files")
        self._actual_num_images = len(tiles)
        self._num_channels = len(channels)
        path = self.path / self.pattern.format(tile=1, channel=1)
        img = skimage.io.imread(path)
        self._tile_size = np.array(img.shape)
        self._dtype = img.dtype


    @property
    def _num_images(self):
        return self._actual_num_images

    @property
    def num_channels(self):
        return self._num_channels

    @property
    def pixel_size(self):
        return 1.0

    @property
    def pixel_dtype(self):
        return self._dtype

    def tile_position(self, i):
        row, col = self.tile_rc(i)
        # Account for serpentine scanning pattern.
        if row % 2 == 1:
            col = self.width - col - 1
        return [row, col] * self.tile_size(i) * (1 - self.overlap)

    def tile_size(self, i):
        return self._tile_size

    def tile_rc(self, i):
        row = i // self.width
        col = i % self.width
        return row, col


class CodexReader(reg.Reader):

    def __init__(self, path, pattern, shape, overlap=0.1):
        self.path = pathlib.Path(path)
        self.pattern = pattern
        self.overlap = overlap
        self.metadata = CodexMetadata(self.path, self.pattern, shape, overlap)

    def read(self, series, c):
        return skimage.io.imread(self.path / self.filename(series, c))

    def filename(self, series, c):
        tile = series + 1
        channel = c + 1
        return self.pattern.format(tile=tile, channel=channel)

