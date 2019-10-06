"""
    sphinxcontrib.editable
    ~~~~~~~~~~~~~~~~~~~~~~

    In-line editable documentation

    :copyright: Copyright 2017 by Metatooling contributors <metatooling@users.noreply.github.com>
    :license: BSD, see LICENSE for details.
"""


if False:
    # For type annotations
    from typing import Any, Dict  # noqa
    from sphinx.application import Sphinx  # noqa

from ._version import __version__


def setup(app):
    # type: (Sphinx) -> Dict[unicode, Any]
    app.add_js_file("js/editable.js")
    app.add_js_file("js/medium-editor.js")
    app.add_css_file("css/medium-editor.css")
    themes = [
        "beagle.css",
        "bootstrap.css",
        "default.css",
        "flat.css",
        "mani.css",
        "roman.css",
        "tim.css",
    ]
    for theme in themes:
        app.add_css_file("css/" + theme)
    return {"version": __version__, "parallel_read_safe": True}
