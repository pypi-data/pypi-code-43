# -*- coding: utf-8 -*-
from publishing_boy.template import render
from publishing_boy.process import (
    file_tuples,
    save_content,
)

from publishing_boy.plugins import run_plugins
"""Main module."""


def transform(obj):
    """This function has to take the object
    and then transform it using plugin functions.

    the output is the object with replaced content
    that suits pelican static site generator.
    """
    name, filepath, fullpath, _ = obj
    context = run_plugins(obj)

    return name, filepath, fullpath, render(context)


def process(folder):
    """Process files in a given folder.

    Create data tuples from files and their contents.
    Pass each tuple thorough transformation function,
    and save it into the  content/ folder.

    """
    for obj in file_tuples(folder):
        save_content(transform(obj))
