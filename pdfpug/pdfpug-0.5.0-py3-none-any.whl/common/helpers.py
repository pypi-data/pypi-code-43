#  MIT License
#
#  Copyright (C) 2019 Nekhelesh Ramananthan
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#  PARTICULAR PURPOSE AND  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
#  AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from typing import Optional


def url(hyperlink: str, text: Optional[str] = None) -> str:
    """
    Create a hyperlink

    .. note::
        If `text` is not provided, the hyperlink will be used as the visible text

    :param hyperlink: URL to resource
    :param text: Text displayed instead of hyperlink
    """
    if text is None:
        text = hyperlink
    return f'<a href="{hyperlink}">{text}</a>'


def bold(text: str) -> str:
    """
    Formats the text to appear bold

    :param text: Text to be bold formatted
    """
    return f"<b>{text}</b>"


def italic(text: str) -> str:
    """
    Formats the text to appear italicized

    :param text: Text to be italic formatted
    """
    return f"<i>{text}</i>"


def underline(text: str) -> str:
    """
    Formats the text to appear underlined

    :param text: Text to be underline formatted
    """
    return f"<u>{text}</u>"


def strike(text: str) -> str:
    """
    Formats the text to appear striked through

    :param text: Text to be strike through formatted
    """
    return f"<strike>{text}</strike>"


def subscript(text: str) -> str:
    """
    Formats the text to appear as a subscript

    :param text: Text to be subscript formatted
    """
    return f"<sub>{text}</sub>"


def superscript(text: str) -> str:
    """
    Formats the text to appear as a superscript

    :param text: Text to be superscript formatted
    """
    return f"<sup>{text}</sup>"
