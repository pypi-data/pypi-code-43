"""
Gradefast is a python framework to speed up evaluation of programming assignments or projects.

The modules inside this package are packed with useful features for the programmer who needs 
to download assignments, evaluate, aggregate and upload the results back to the portal. 

Gradefast is programming language agnostic and includes features like error logging, plagiarism 
checking, and security of evaluation environment. 

"""

import logging
from .__version__ import __version__

top_logger = logging.getLogger(__name__)
