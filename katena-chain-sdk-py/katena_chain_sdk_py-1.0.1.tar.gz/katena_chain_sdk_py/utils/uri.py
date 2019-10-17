"""
Copyright (c) 2019, TransChain.

This source code is licensed under the Apache 2.0 license found in the
LICENSE file in the root directory of this source tree.
"""


def get_uri(base_path: str, paths: []) -> str:
    """ Joins the base path and paths array and adds the query values to return a new uri."""
    items = [base_path, *paths]
    return "/".join([(u.strip("/") if index + 1 < len(items) else u.lstrip("/")) for index, u in enumerate(items)])
