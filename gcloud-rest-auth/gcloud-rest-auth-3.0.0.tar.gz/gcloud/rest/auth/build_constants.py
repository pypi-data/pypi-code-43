from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
# Internal build variable to help choose the correct target code for
# syntactically differing code in AIO and REST builds
from future import standard_library
standard_library.install_aliases()
BUILD_GCLOUD_REST = not __package__ or 'rest' in __package__
