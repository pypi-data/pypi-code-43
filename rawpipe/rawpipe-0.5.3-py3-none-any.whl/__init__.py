"""A collection of camera raw processing algorithms.

A collection of reference ISP algorithms, sufficient for producing a reasonably
good looking image from raw sensor data. Each algorithm takes in a frame in RGB
or raw format and returns a modified copy of the frame. The frame is expected to
be a NumPy float array with either 2 or 3 dimensions, depending on the function.

Example:
  algs = rawpipe.Algorithms(verbose=True)
  raw = algs.linearize(raw, blacklevel=64, whitelevel=1023)
  rgb = algs.demosaic(raw, "RGGB")
  rgb = algs.wb(rgb, [1.5, 2.0])
  rgb = algs.quantize(rgb, 255)
"""

from .rawpipe import Algorithms

__version__ = "0.5.3"
__all__ = ["Algorithms"]
