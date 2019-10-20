from .marc import Converter

__author__ = 'zhv'
__license__ = 'GPLv3'
__version__ = '0.0.1'

converter = Converter()
to_aleph = converter.to_aleph
to_marc = converter.to_marc
