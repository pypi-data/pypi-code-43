# -*- coding: utf-8 -*-
"""cleanNLP
"""

from __future__ import absolute_import
from os import environ

from . import corenlp
from . import spacy

__version__ = "1.0.0"

environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
