"""
    sphinxcontrib.editable
    ~~~~~~~~~~~~~~~~~~~~~~

    In-line editable documentation

    :copyright: Copyright 2017 by Metatooling contributors <metatooling@users.noreply.github.com>
    :license: BSD, see LICENSE for details.
"""

import pbr.version

if False:
    # For type annotations
    from typing import Any, Dict  # noqa
    from sphinx.application import Sphinx  # noqa

__version__ = pbr.version.VersionInfo("editable").version_string()


def setup(app):
    # type: (Sphinx) -> Dict[unicode, Any]
    app.add_js_file("js/editable.js")
    return {"version": __version__, "parallel_read_safe": True}
