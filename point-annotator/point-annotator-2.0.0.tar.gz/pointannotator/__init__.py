from pkg_resources import DistributionNotFound, get_distribution

__import__("pkg_resources").declare_namespace(__name__)
try:
    __version__ = get_distribution('point-annotator').version
except DistributionNotFound:
    # package is not installed
    pass
