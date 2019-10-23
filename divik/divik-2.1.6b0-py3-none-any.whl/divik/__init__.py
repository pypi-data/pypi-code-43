__version__ = "2.1.6b"

from ._sklearn import DiviK
from .kmeans import AutoKMeans, KMeans
from .feature_selection import GMMSelector, HighAbundanceAndVarianceSelector
