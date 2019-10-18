import sys
if sys.version_info >= (3, 3):
    from unittest.mock import MagicMock, Mock
else:
    from mock import MagicMock, Mock