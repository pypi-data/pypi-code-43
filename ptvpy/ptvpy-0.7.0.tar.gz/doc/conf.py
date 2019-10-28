"""Sphinx configuration file for PtvPy.

Furthermore this file extends sphinx's functionality and applies several patches:

- Adds the ``click-cmd`` directive and role. This directive works similar to the
  directives added by the autodoc extension but for click.Commands which can then be
  referenced using the role. See :class:`ClickCommandDirective` for more details.
- Adds ``theme_overrides.css`` and ``copybutton.js`` to the used sphinx_rtd_theme.
- Adds the function hook :func:`linkcode_resolve` which ensures code links to the
  repository on GitLab are properly handled.
- Adds several patches to ensure that numba-jitted functions are correctly documented
  (see :func:`wrap_get_documenter`), docstring sanitation (see
  :func:`wrap_mangle_docstrings`) and other small tweaks.

PtvPy must be installed.

Possible configuration options for sphinx are documented here:
http://www.sphinx-doc.org/en/master/usage/configuration.html
"""


import inspect
import sys
import warnings
from datetime import datetime
from functools import wraps
from pathlib import Path

import click
import numba.dispatcher
import sphinx.ext.autodoc
import sphinx.ext.autosummary
import sphinx.ext.intersphinx
from numpydoc import numpydoc
from sphinx.util import logging

import ptvpy


# Make local sphinx extensions in current directory visible
sys.path.append(str(Path(__file__).parent))


logger = logging.getLogger(__name__)


# Minimal Sphinx version.
needs_sphinx = "1.6"
if sphinx.__version__[0] >= "2":
    warnings.warn(
        "Using sphinx 2.0 or higher. sphinx_rtd_theme and numpydoc may not be fully "
        "compatible yet and the theme might render incorrectly. "
        "See https://gitlab.com/tud-mst/ptvpy/issues/14."
    )

# Used Sphinx extension module names here.
extensions = [
    # http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
    "sphinx.ext.autodoc",
    # http://www.sphinx-doc.org/en/master/usage/extensions/doctest.html
    "sphinx.ext.doctest",
    # http://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html
    "sphinx.ext.autosummary",
    # http://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.mathjax
    "sphinx.ext.mathjax",
    # http://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html
    "sphinx.ext.linkcode",
    # http://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
    "sphinx.ext.intersphinx",
    # https://numpydoc.readthedocs.io/
    "numpydoc",
    "sphinx_click_cmd",
]

# (sphinx.ext.autosummary) Boolean indicating whether to scan all found documents for
# autosummary directives, and to generate stub pages for each. Can also be a list of
# documents for which stub pages should be generated. The new files will be placed in
# the directories specified in the :toctree: options of the directives.
autosummary_generate = True

# (sphinx.ext.autdoc) The default options for autodoc directives. They are applied to
# all autodoc directives automatically. Setting None or True to the value is equivalent
# to giving only the option name to the directives.
autodoc_default_options = {"show-inheritance": True, "private-members": True}

# (sphinx.ext.autdoc) This value selects if automatically documented members are sorted
# alphabetical (value 'alphabetical'), by member type (value 'groupwise') or by source
# order (value 'bysource'). The default is alphabetical.
autodoc_member_order = "alphabetical"

# (intersphinx) This config value contains the locations and names of other projects
# that should be linked to in this documentation.Relative local paths for target
# locations are taken as relative to the base of the built documentation, while relative
# local paths for inventory locations are taken as relative to the source directory.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "h5py": ("http://docs.h5py.org/en/stable/", None),
    "cerberus": ("http://docs.python-cerberus.org/en/stable/", None),
    # "pandas": ("https://pandas.pydata.org/pandas-docs/stable/", None),
    # "numpy": ("https://docs.scipy.org/doc/numpy/", None),
    # "numba": ("https://numba.pydata.org/numba-doc/latest/", None),
    # "matplotlib": ("https://matplotlib.org/", None),
    # "trackpy": ("http://soft-matter.github.io/trackpy/v0.4.2/", None),
}

# (numpydoc) Whether to show all members of a class in the Methods and Attributes
# sections automatically. True by default.
numpydoc_show_class_members = False

# Paths containing templates, relative to this directory.
templates_path = ["_templates"]

# Suffix(es) of source filenames.
source_suffix = ".rst"

# Master toctree document.
master_doc = "index"

# General information about the project.
project = "PtvPy"
copyright = f"2018-{datetime.now().year}, PtvPy developers"
author = "PtvPy Developers"

# The short X.Y version.
version = ptvpy.__version__.split("+")[0]

# The full version, including alpha/beta/rc tags.
release = ptvpy.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["build", "Thumbs.db", ".DS_Store"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# A boolean that decides whether module names are prepended to all object names
# (for object types where a “module” of some kind is defined), e.g. for
# py:function directives. Default is True.
add_module_names = True

# A boolean that decides whether parentheses are appended to function and
# method role text (e.g. the content of :func:`input`) to signify that the
# name is callable. Default is True.
add_function_parentheses = False

# The theme to use for HTML and HTML Help pages.
html_theme = "sphinx_rtd_theme"

# See https://sphinx-rtd-theme.readthedocs.io/en/latest/configuring.html
html_theme_options = {"logo_only": True}

# https://docs.readthedocs.io/en/stable/vcs.html#gitlab
html_context = {
    "display_gitlab": True,
    "gitlab_user": "tud-mst",
    "gitlab_repo": "ptvpy",
    "gitlab_version": "master",
    "conf_py_path": "/doc/",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Name of an image file (path relative to the configuration directory) that is
# the logo of the docs. It is placed at the top of the sidebar; its width
# should therefore not exceed 200 pixels.
html_logo = "_static/logo.svg"

# Name of an image file (path relative to the configuration directory) that is
# the favicon of the docs. Modern browsers use this as the icon for tabs,
# windows and bookmarks.
html_favicon = "_static/icon.png"


def linkcode_resolve(domain, info):
    """Resolve link for code objects.

    This function is a hook called by the sphinx extension linkcode [1]_.
    Loosely inspired by a function in NumPy [2]_.

    Parameters
    ----------
    domain : str
        Specifies the language domain of the given object.
    info : dict
        A dictionary describing the object.

    Returns
    -------
    url : str
        An URL to the source code.

    References
    ---------
    .. [1] http://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html
    .. [2] https://github.com/numpy/numpy/blob/cbf3a081271a43e980e3c2f76625deb43fd53922/doc/source/conf.py#L303-L357
    """  # noqa: E501
    if domain not in ["py", "std"] or "module" not in info or "fullname" not in info:
        return None

    # Get reference to the object, start with the module
    obj = sys.modules.get(info["module"])
    for part in info["fullname"].split("."):
        try:
            obj = getattr(obj, part)
        except AttributeError:
            # Not all attributes exist, e.g. instance attributes
            return None
    if isinstance(obj, property):
        # Skip properties which don't seem to be supported by inspect's functions
        return None
    if isinstance(obj, click.Command):
        # Unwrap click.Command which doesn't have a __wrapped__ attribute
        obj = obj.callback
    # Strip decorators which would resolve to the source of the decorator
    obj = inspect.unwrap(obj)

    revision = ptvpy._version_info["full-revisionid"]
    file = info["module"].replace(".", "/")
    try:
        source, start_line = inspect.getsourcelines(obj)
    except TypeError:
        # Skip unexpected types, occurs when obj isn't a module, class, method,
        # function, etc.
        return None
    stop_line = start_line + len(source) - 1

    template = (
        "https://gitlab.com/tud-mst/ptvpy/blob/{revision}/src/{file}.py#L{start}-{stop}"
    )
    url = template.format(
        revision=revision, file=file, start=start_line, stop=stop_line
    )
    return url


# Make solver available to sphinx_click_cmd as well
sphinx_click_cmd_resolve = linkcode_resolve


# Ensure that instance attributes don't display " = None"
# See here: https://github.com/sphinx-doc/sphinx/issues/2044
sphinx.ext.autodoc.InstanceAttributeDocumenter.add_directive_header = (
    sphinx.ext.autodoc.ClassLevelDocumenter.add_directive_header
)


# Ensure that numba-jitted functions are correctly documented by replacing
# them with the original wrapped pure Python function at the appropriate
# places in sphinx.ext.autosummary and sphinx.ext.autodoc
def wrap_get_documenter(func):
    @wraps(func)
    def wrapper(*args):
        # len(args) may be 2 or 3, obj is alwayss at position [-2]
        obj = args[-2]
        if isinstance(obj, numba.dispatcher.Dispatcher):
            args = list(args)
            args[-2] = obj.py_func
        return func(*args)

    return wrapper


sphinx.ext.autosummary.get_documenter = wrap_get_documenter(
    sphinx.ext.autosummary.get_documenter
)


class FunctionDocumenter(sphinx.ext.autodoc.FunctionDocumenter):
    def import_object(self):
        return_value = super().import_object()
        if isinstance(self.object, numba.dispatcher.Dispatcher):
            self.object = self.object.py_func
        return return_value


sphinx.ext.autodoc.FunctionDocumenter = FunctionDocumenter


def wrap_mangle_docstrings(func):
    r"""
    Remove any lines containing the characters \b and \f inside docstrings
    before numpydoc has a chance to process docstrings.
    """

    @wraps(func)
    def wrapper(app, what, name, obj, options, lines):
        #  Modifying `lines` inplace while iterating in a save manner
        i = 0
        while i < len(lines):
            if "\b" in lines[i] or "\f" in lines[i]:
                lines.pop(i)
            else:
                i += 1
        return func(app, what, name, obj, options, lines)

    return wrapper


numpydoc.mangle_docstrings = wrap_mangle_docstrings(numpydoc.mangle_docstrings)


# Emitted when numpydoc tries to process signatures in
# numpydoc.numpydoc.mangle_signature and the docstrings contain the same offending
# characters as in the patch above. This is harmless.
warnings.filterwarnings(
    action="ignore",
    message="Unknown section .* in the docstring.*",
    category=UserWarning,
    module="numpydoc.docscrape",
)


def patch_missing_reference_target(app, env, node, contnode):
    """Patch missing reference targets for intersphinx.

    sphinx.ext.autodoc generates references with targets that may not match the
    target scheme used in the external libraries objects.inv (e.g. when referencing
    a base class). The scheme is usually reflects whether Python objects are
    documented with their full, partial or no module path.

    This function should be connected to Sphinx's "missing-reference" event.
    """
    target = node["reftarget"]
    if "cerberus" in target:
        # Only keep top-level module from module path
        *module_path, object_name = target.split(".")
        new_target = module_path[0] + "." + object_name
        node["reftarget"] = new_target
    elif "h5py" in target:
        # Drop module path entirely
        *_, object_name = target.split(".")
        node["reftarget"] = object_name
    else:
        return

    # Attempt to resolve link with patched target
    return sphinx.ext.intersphinx.missing_reference(app, env, node, contnode)


def setup(app):
    app.add_javascript("copybutton.js")
    app.add_css_file("theme_overrides.css")
    app.add_object_type(
        "profile-option",
        "profile-option",
        objname="profile option",
        indextemplate="single: %s; configuration value",
    )
    app.connect("missing-reference", patch_missing_reference_target)
