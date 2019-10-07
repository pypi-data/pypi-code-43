"""
Expose resources prvided by the package
"""

from __future__ import annotations

import os


def resource_provider_path(provider_path:str) -> str:
    this_dir = os.path.abspath(os.path.dirname(__file__))
    resource_path = os.path.abspath(this_dir + os.path.sep + provider_path)
    assert os.path.exists(resource_path), f"Missing provider_path: {provider_path}"
    return resource_path
