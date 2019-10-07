from .mitomap import MitomapFileSource
from .uniprot import UniprotFileSource

source_name_map = {"mitomap": MitomapFileSource, "uniprot": UniprotFileSource}

__all__ = ("MitomapFileSource", "UniprotFileSource")
