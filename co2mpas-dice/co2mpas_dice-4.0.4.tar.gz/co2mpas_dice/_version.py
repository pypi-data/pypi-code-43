# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
# Copyright 2016-2017 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl


#: Authoritative project's PEP 440 version.
__version__ = version = "4.0.4"  # Also update README.rst,

# Please UPDATE TIMESTAMP WHEN BUMPING VERSIONS AND BEFORE RELEASE.
#: Release date.
__updated__ = updated = "2019-10-24 00:40:00"


if __name__ == '__main__':
    import sys
    out = ';'.join(
        eval(a[2:].replace('-', '_')) for a in sys.argv[1:] if a[:2] == '--'
    )
    sys.stdout.write(out)
