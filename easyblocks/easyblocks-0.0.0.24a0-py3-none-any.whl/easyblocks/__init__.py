#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .easyblocks import Blockchain
import logging

__version__ = '0.0.0.24a'

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)-15s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.info(f'EasyBlocks v{__version__}')
