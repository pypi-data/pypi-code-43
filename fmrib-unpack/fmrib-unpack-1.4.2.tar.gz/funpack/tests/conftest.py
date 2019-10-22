#!/usr/bin/env python
#
# conftest.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#

import inspect

import funpack.fileinfo  as fileinfo
import funpack.hierarchy as hierarchy
import funpack.coding    as coding


def fake_cache_clear():
    pass


fileinfo.sniff              = inspect.unwrap(fileinfo.sniff)
fileinfo.fileinfo           = inspect.unwrap(fileinfo.fileinfo)
hierarchy.loadHierarchyFile = inspect.unwrap(hierarchy.loadHierarchyFile)
coding.loadCodingFile       = inspect.unwrap(coding.loadCodingFile)

fileinfo.sniff             .cache_clear = fake_cache_clear
fileinfo.fileinfo          .cache_clear = fake_cache_clear
hierarchy.loadHierarchyFile.cache_clear = fake_cache_clear
coding.loadCodingFile      .cache_clear = fake_cache_clear
