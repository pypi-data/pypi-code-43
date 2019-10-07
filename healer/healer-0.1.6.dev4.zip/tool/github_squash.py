#!/usr/bin/env python

"""
Squash github commits starting from a point
"""

from __future__ import annotations

from devrepo import shell

point = "c57f2123fbdd23e1ce23ba52e251e7f75fd799cd"
message = "Develop"

shell(f"git reset --soft {point}")
shell(f"git add --all")
shell(f"git commit --message='{message}'")
shell(f"git push --force --follow-tags")
