"""
    sphinxcontrib.editable
    ~~~~~~~~~~~~~~~~~~~~~~

    In-line editable documentation

    :copyright: Copyright 2017 by Metatooling contributors <metatooling@users.noreply.github.com>
    :license: BSD, see LICENSE for details.
"""
import os.path

from sphinx.util.fileutil import copy_asset
import importlib_resources

import sphinxcontrib.editable._static.css
import sphinxcontrib.editable._static.css.themes
import sphinxcontrib.editable._static.js

from ._version import __version__


if False:
    # For type annotations
    from typing import Any, Dict  # noqa
    from sphinx.application import Sphinx  # noqa


JS_FILES = ["editable.js", "medium-editor.js"]
CSS_FILES = ["medium-editor.css"]
THEME_FILES = [
    "beagle.css",
    "bootstrap.css",
    "default.css",
    "flat.css",
    "mani.css",
    "roman.css",
    "tim.css",
]


def copy_asset_files(app, exc):
    if exc is not None:  # build succeeded:
        return

    outdir = os.path.join(app.outdir, "_static/js")
    os.makedirs(outdir, exist_ok=True)
    for file in JS_FILES:
        with importlib_resources.path(sphinxcontrib.editable._static.js, file) as path:
            copy_asset(str(path), str(outdir))

    outdir = os.path.join(app.outdir, "_static/css")
    os.makedirs(outdir, exist_ok=True)
    for file in CSS_FILES:
        with importlib_resources.path(sphinxcontrib.editable._static.css, file) as path:
            copy_asset(str(path), str(outdir))


    outdir = os.path.join(app.outdir, "_static/css/themes")
    os.makedirs(outdir, exist_ok=True)
    for file in THEME_FILES:
        with importlib_resources.path(sphinxcontrib.editable._static.css.themes, file) as path:
            copy_asset(str(path), str(outdir))


def setup(app):
    # type: (Sphinx) -> Dict[unicode, Any]
    for file in JS_FILES:
        app.add_js_file("js/" + file)
    for file in CSS_FILES:
        app.add_css_file("css/" + file)

    app.connect("build-finished", copy_asset_files)

    return {"version": __version__, "parallel_read_safe": True}
