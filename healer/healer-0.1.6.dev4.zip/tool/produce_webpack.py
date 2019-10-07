#!/usr/bin/env python

"""
Provision embedded resources
"""

from __future__ import annotations

from devrepo import base_dir, shell

prefix = 'src/main/healer/station/web_npm'

shell(f"npm install --prefix {prefix}")
shell(f"npm run build --prefix {prefix}")
