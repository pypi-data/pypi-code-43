import os
from datetime import datetime
"""Here are functions that serve the
role of plugins. Each function
accepts tuple object with:
- filename
- content
- path

Those functions are loaded to the program
by a decorator, during module loading.
Functions are stored inside a list.
"""

PLUGINS = []


def register_plugin(fn):
    """This decorator add a function to PLUGINS
    list.

    Order of plugins is not important"""
    global PLUGINS
    PLUGINS.append(fn)

    return fn


@register_plugin
def content_function(obj):
    """Just return content"""
    _, _, _, content = obj

    return 'content', content


@register_plugin
def title_extractior(obj):
    """Extract title from content.
    Use NTLK to do stuff with text. - maybe later

    for know i will use first sentence in text

    @return: 'title', generated_content"""
    _, _, _, content = obj

    if not content:
        return 'title', ''

    # fallback
    cut = 40 if len(content) >= 40 else len(content)
    title = content[:cut].strip() + " ..."

    pos = content.find(".")
    if pos != -1:
        title = content[:pos].strip()

    return 'title', title


@register_plugin
def creation_date(obj):
    """Extract date when the file was
    created.

    @return: 'date', date(YYYY-mm-dd HH:MM:SS)"""
    _, _, abspath, _ = obj
    return 'cdate', datetime.fromtimestamp(os.path.getctime(abspath))


@register_plugin
def modified_date(obj):
    """Extract date when the file was
    modified.

    @return: 'modified', date(YYYY-mm-dd HH:MM:SS)"""
    _, _, abspath, _ = obj
    return 'mdate', datetime.fromtimestamp(os.path.getmtime(abspath))


@register_plugin
def category_extract(obj):
    """Extract category. Category are
    the folder names in path file.

    @return: 'category', 'String, Separated, by'
    """
    _, filepath, _, _ = obj
    names = filter(None, os.path.dirname(filepath).split("/"))
    categories = ", ".join(map(str.capitalize, names))

    return 'categories', categories


@register_plugin
def authors(obj):
    """Return authors"""
    return 'authors', os.environ.get('PB_AUTHOR', '')


def run_plugins(obj):
    """Run all plugins on object"""
    global PLUGINS
    return {key: value for key, value in [plugin(obj) for plugin in PLUGINS]}
