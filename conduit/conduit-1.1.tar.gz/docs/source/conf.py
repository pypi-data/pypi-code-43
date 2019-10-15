# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

SOURCE_PATH = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(SOURCE_PATH, "..", ".."))

sys.path.insert(0, PROJECT_ROOT)

from conduit  import get_version

# -- Project information -----------------------------------------------------

project = 'Conduit'
copyright = '2019, Kevin D. Jones and PingThings'
author = 'Kevin D. Jones and PingThings'

# The full version, including alpha/beta/rc tags
version = get_version()
release = "v{}".format(version)


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'numpydoc',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    'Thumbs.db', '.DS_Store', '*.py',
]

# The suffix(es) of source filenames
# You can specify multiple suffix as a list of strings
source_suffix = '.rst'

# The encoding of source files
source_encoding = 'utf-8-sig'

# The master toctree document
master_doc = 'index'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'show_powered_by': False,
    'github_user': 'PingThingsIO',
    'github_repo': 'conduit',
    'travis_button': False,
    'github_banner': False,
    'show_related': False,
    'note_bg': '#FFF59C',
    'description': 'Stream transformation utilities for Power Engineering analytics',
    'extra_nav_links': {
        "BTrDB": "http://btrdb.io",
        "btrdb-python": "https://btrdb.readthedocs.io/en/latest/",
        "PingThings": "https://www.pingthings.io",
    },
    'show_relbars': True,
}


# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#
html_favicon = "_static/favicon.ico"


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'conduitdoc'

# -- Extensions configuration -------------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# Autodoc requires numpy to skip class members otherwise we get an exception:
# toctree contains reference to nonexisting document
# See: https://github.com/phn/pytpm/issues/3#issuecomment-12133978
numpydoc_show_class_members = False

# Locations of objects.inv files for intersphinx extension that auto-links
# to external api docs.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'matplotlib': ('http://matplotlib.org/', None),
    'scipy': ('http://docs.scipy.org/doc/scipy/reference', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'cycler': ('http://matplotlib.org/cycler/', None),
    'btrdb': ('https://btrdb.readthedocs.io/en/latest/', None),
}