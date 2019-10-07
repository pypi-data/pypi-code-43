#!/usr/bin/env python

"""
Produce JS from PY.
"""

from __future__ import annotations

from devrepo import shell

main = 'src/main/healer/station/client/arkon.py'

shell(f"transcrypt {main} --map --nomin --dassert")
